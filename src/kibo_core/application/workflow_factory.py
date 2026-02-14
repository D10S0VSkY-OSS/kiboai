from typing import Any, Dict, List
from kibo_core.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kibo_core.domain.blueprint import AgentConfig
from kibo_core.application.factory import agent_factory, _resolve_llm_params
from kibo_core.infrastructure.adapters.base import BaseAgentAdapter


def _compile_workflow_to_crewai(
    config: WorkflowConfig, api_key: str
) -> BaseAgentAdapter:
    from crewai import Crew, Task, Process
    from kibo_core.infrastructure.adapters.crewai_adapter import CrewAIAdapter

    # Sort tasks sequentially for now since CrewAI is mainly sequential/hierarchical
    # A topological sort would be ideal here if 'next' pointers are complex

    # Simple linear resolution based on 'next' pointer
    ordered_steps = []
    current_step_id = config.start_step

    # Map for easy access
    step_map = {step.id: step for step in config.steps}

    visited = set()
    while current_step_id:
        if current_step_id in visited:
            break  # Loop detected
        visited.add(current_step_id)

        step = step_map.get(current_step_id)
        if not step:
            break

        ordered_steps.append(step)

        # Simple linear: follow the first 'next' if it's a list or string
        next_val = step.next
        if isinstance(next_val, list) and next_val:
            current_step_id = next_val[0]
        elif isinstance(next_val, str):
            current_step_id = next_val
        else:
            current_step_id = None

    tasks = []
    agents = []

    for step in ordered_steps:
        # Create the underlying agent using existing factory but force engine to 'crewai' to be safe?
        # Actually user might want to mix engines but CrewAI expects CrewAI Agents.
        # We must cast/create a CrewAI agent from the config.
        # So we clone the config and set agent='crewai' to reuse the factory logic
        step_agent_config = step.agent.model_copy()
        step_agent_config.agent = "crewai"

        # We need the inner CrewAI Agent object, not the adapter.
        # The factory returns an Adapter. We need to peek inside or
        # refactor factory to return raw agent.
        # For now, let's use the factory's internal helper if possible or
        # assume the adapter exposes the agent.

        # HACK: Create the adapter and extract the underlying agent
        # Ideally factory should be split into create_agent_adapter and create_agent_instance
        adapter = agent_factory(step_agent_config, api_key)

        # CrewAIAdapter stores it in self.crew usually, but here we are creating a single agent
        # Wait, agent_factory for crewai returns a CrewAIAdapter which wraps a Crew.
        # We need an Agent, not a Crew.

        # Re-implementing simplified agent creation to avoid wrapping in a Crew
        from crewai import Agent as CrewAgent
        from crewai.llm import LLM

        # Use factory logic roughly
        base_url, final_key = _resolve_llm_params(step_agent_config, api_key)
        llm = LLM(model=step_agent_config.model, api_key=final_key, base_url=base_url)
        c_agent = CrewAgent(
            role=step_agent_config.name,
            goal=step_agent_config.instructions,
            backstory=step_agent_config.description,
            llm=llm,
        )

        agents.append(c_agent)

        task = Task(
            description=step.instruction,
            agent=c_agent,
            expected_output="Completion of the task.",
        )
        tasks.append(task)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        # Native Extensions Pass-through
        **config.native_extensions,
    )

    # Hook implementation
    if config.on_before_compile and callable(config.on_before_compile):
        # For CrewAI, "compile" is basically creating the Crew object.
        # Since we just created it, we can pass it to the hook for post-creation modification
        # or we could have passed the tasks/agents list before creation.
        # Let's pass the created crew instance.
        config.on_before_compile(crew)

    return CrewAIAdapter(crew)


def _compile_workflow_to_langgraph(
    config: WorkflowConfig, api_key: str
) -> BaseAgentAdapter:
    from langgraph.graph import StateGraph, START, END
    from kibo_core.infrastructure.adapters.langgraph_adapter import LangGraphAdapter
    from typing import Annotated, TypedDict, Union
    from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
    import operator
    from kibo_core.application.factory import agent_factory

    # Define State
    class AgentState(TypedDict):
        messages: Annotated[List[BaseMessage], operator.add]
        current_step: str
        outputs: Dict[str, str]

    graph_builder = StateGraph(AgentState)

    # Create Nodes
    for step in config.steps:

        # Create the agent for this step
        # We can use any supported agent type here!
        # LangGraph works best with LangChain runnables, but we can wrap others.
        # For simplicity, let's force creation of a LangChain agent
        # or use Kibo's unified execution.

        step_agent_config = step.agent.model_copy()
        # Prefer langchain for native integration if not specified
        if step_agent_config.agent == "crewai":
            step_agent_config.agent = (
                "langchain"  # Convert to LC for graph compatibility easily
            )

        # Create the executable adapter
        agent_adapter = agent_factory(step_agent_config, api_key)

        def make_node_func(adapter: BaseAgentAdapter, instruction: str, step_id: str):
            def node_func(state: AgentState):
                # Construct input
                msgs = state.get("messages", [])
                last_msg = msgs[-1].content if msgs else ""

                # Combine instruction with previous context
                combined_input = f"Instruction: {instruction}\nContext: {last_msg}"

                # Execute Kibo Agent
                # We need to construct a Request-like object object
                # but adapters expect AgentRequest.
                from kibo_core.domain.entities import AgentRequest, AgentContext
                import uuid

                req = AgentRequest(
                    input_data=combined_input,
                    request_id=uuid.uuid4(),
                    context=AgentContext(
                        workflow_id=uuid.uuid4(),  # Dummy ID for now
                        step_id=uuid.uuid4(),
                    ),
                )

                result = adapter.execute(req)

                output = result.output_data

                return {
                    "messages": [HumanMessage(content=str(output))],
                    "current_step": step_id,
                    "outputs": {step_id: str(output)},
                }

            return node_func

        # Add node to graph
        node_name = step.id
        graph_builder.add_node(
            node_name, make_node_func(agent_adapter, step.instruction, step.id)
        )

    # Create Edges
    # 1. Start edge
    if config.start_step:
        graph_builder.add_edge(START, config.start_step)

    # 2. Step edges
    for step in config.steps:
        if step.next:
            if isinstance(step.next, str):
                graph_builder.add_edge(step.id, step.next)
            elif isinstance(step.next, list):
                # Branching logic would go here (Router)
                # For now, take first
                graph_builder.add_edge(step.id, step.next[0])
        else:
            graph_builder.add_edge(step.id, END)

    # Hook implementation: Allow user to modify graph_builder before compilation
    if config.on_before_compile and callable(config.on_before_compile):
        config.on_before_compile(graph_builder)

    # Native Extensions Pass-through for compile()
    # e.g. checkpointer, interrupt_before, etc.
    compile_kwargs = config.native_extensions or {}

    compiled_graph = graph_builder.compile(**compile_kwargs)

    return LangGraphAdapter(compiled_graph)


from kibo_core.application.workflow_factory_agno import _compile_workflow_to_agno


def workflow_factory(config: WorkflowConfig, api_key: str = None) -> BaseAgentAdapter:
    """
    Directly returns an Adapter (like LangGraphAdapter or CrewAIAdapter)
    that wraps the compiled workflow.
    """
    if config.engine == "langgraph":
        return _compile_workflow_to_langgraph(config, api_key)
    elif config.engine == "crewai":
        return _compile_workflow_to_crewai(config, api_key)
    elif config.engine == "agno":
        return _compile_workflow_to_agno(config, api_key)
    else:
        raise ValueError(f"Unsupported workflow engine: {config.engine}")
