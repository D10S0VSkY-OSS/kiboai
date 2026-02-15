from typing import Any, Dict, List, Optional
import uuid
from kibo_core.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kibo_core.domain.blueprint import AgentConfig
from kibo_core.application.factory import agent_factory, _resolve_llm_params
from kibo_core.infrastructure.adapters.base import BaseAgentAdapter
from kibo_core.domain.entities import AgentRequest, AgentContext


def _compile_workflow_to_crewai(
    config: WorkflowConfig, api_key: str
) -> BaseAgentAdapter:
    from crewai import Crew, Task, Process
    from kibo_core.infrastructure.adapters.crewai_adapter import CrewAIAdapter

    ordered_steps = []
    current_step_id = config.start_step

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
        step_agent_config = step.agent.model_copy()
        step_agent_config.agent = "crewai"

        from crewai import Agent as CrewAgent
        from crewai.llm import LLM

        if not isinstance(step_agent_config.model, str):
            llm = step_agent_config.model
        else:
            base_url, final_key = _resolve_llm_params(step_agent_config, api_key)
            llm = LLM(
                model=step_agent_config.model, api_key=final_key, base_url=base_url
            )

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
        **config.native_extensions,
    )

    if config.on_before_compile and callable(config.on_before_compile):
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

    class AgentState(TypedDict):
        messages: Annotated[List[BaseMessage], operator.add]
        current_step: str
        outputs: Dict[str, str]

    graph_builder = StateGraph(AgentState)

    for step in config.steps:

        step_agent_config = step.agent.model_copy()
        if step_agent_config.agent == "crewai":
            step_agent_config.agent = (
                "langchain"  # Convert to LC for graph compatibility easily
            )

        agent_adapter = agent_factory(step_agent_config, api_key)

        def make_node_func(adapter: BaseAgentAdapter, instruction: str, step_id: str):
            def node_func(state: AgentState):
                msgs = state.get("messages", [])
                last_msg = msgs[-1].content if msgs else ""

                combined_input = f"Instruction: {instruction}\nContext: {last_msg}"

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

        node_name = step.id
        graph_builder.add_node(
            node_name, make_node_func(agent_adapter, step.instruction, step.id)
        )

    if config.start_step:
        graph_builder.add_edge(START, config.start_step)

    for step in config.steps:
        if step.next:
            if isinstance(step.next, str):
                graph_builder.add_edge(step.id, step.next)
            elif isinstance(step.next, list):
                graph_builder.add_edge(step.id, step.next[0])
        else:
            graph_builder.add_edge(step.id, END)

    if config.on_before_compile and callable(config.on_before_compile):
        config.on_before_compile(graph_builder)

    compile_kwargs = config.native_extensions or {}

    compiled_graph = graph_builder.compile(**compile_kwargs)

    return LangGraphAdapter(compiled_graph)


from kibo_core.application.workflow_factory_agno import _compile_workflow_to_agno


def workflow_factory(
    config: WorkflowConfig, api_key: Optional[str] = None
) -> BaseAgentAdapter:
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
