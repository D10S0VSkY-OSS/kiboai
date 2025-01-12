import os
from typing import Any, Callable
from kibo_core.domain.blueprint import AgentConfig
from kibo_core.infrastructure.adapters.base import LazyAgentAdapter
from crewai.llm import LLM

def _resolve_llm_params(bp: AgentConfig, api_key: str):
    """
    Central logic to determine Model, Base URL and API Key.
    Prioritizes Kibo Proxy (LiteLLM) if configured, then Framework-specific defaults.
    """
    base_url = bp.config.get("base_url")
    final_api_key = api_key or bp.config.get("api_key")

    if not base_url:
        proxy_url = os.getenv("KIBO_PROXY_URL") # e.g. http://localhost:4000
        if proxy_url:
            base_url = proxy_url
            if not final_api_key: final_api_key = "sk-kibo-proxy" # Dummy key for proxy
    
    return base_url, final_api_key


def _create_crewai_agent(bp: AgentConfig, api_key: str):
    from crewai import Agent, Task, Crew, Process
    from kibo_core.infrastructure.adapters.crewai_adapter import CrewAIAdapter
    
    base_url, final_key = _resolve_llm_params(bp, api_key)
    
    llm = LLM(model=bp.model, api_key=final_key, base_url=base_url)
    
    verbose = bp.config.get("verbose", True)
    allow_delegation = bp.config.get("allow_delegation", False)
    tools = bp.config.get("tools", [])
    
    researcher = Agent(
        role=bp.name, # Use name as role identifier usually
        goal=bp.instructions,
        backstory=bp.description,
        verbose=verbose,
        allow_delegation=allow_delegation,
        llm=llm,
        tools=tools
    )
    
    
    task = Task(
        description=f"Parse the following input and Execute instructions: {bp.instructions}. \nInput: {{topic}}",
        agent=researcher,
        expected_output="Result of the instructions."
    )
    
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        verbose=verbose,
        process=Process.sequential
    )
    
    return CrewAIAdapter(crew)

def _create_agno_agent(bp: AgentConfig, api_key: str):
    from agno.agent import Agent
    from kibo_core.infrastructure.adapters.agno_adapter import AgnoAdapter
    from agno.models.openai import OpenAIChat
    
    base_url, final_key = _resolve_llm_params(bp, api_key)

    model = OpenAIChat(id=bp.model, base_url=base_url, api_key=final_key)
    
    agent = Agent(
        model=model,
        description=bp.description,
        instructions=bp.instructions,
        markdown=bp.config.get("markdown", True),
        tools=bp.config.get("tools", [])
    )
    
    return AgnoAdapter(agent)

def _create_pydantic_agent(bp: AgentConfig, api_key: str):
    import os
    from pydantic_ai import Agent
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider
    from kibo_core.infrastructure.adapters.pydantic_ai_adapter import PydanticAIAdapter
    
    base_url, final_key = _resolve_llm_params(bp, api_key)
    
    model_arg = bp.model
    
    sys_prompt = f"{bp.description}\n\n{bp.instructions}"

    provider = OpenAIProvider(base_url=base_url, api_key=final_key)
    
    if "openai:" in model_arg:
        model_arg = model_arg.replace("openai:", "")
        
    model = OpenAIModel(model_arg, provider=provider)
    
    agent = Agent(
        model, 
        system_prompt=sys_prompt
    )
    
    return PydanticAIAdapter(agent)

def _create_langchain_agent(bp: AgentConfig, api_key: str):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableLambda
    from kibo_core.infrastructure.adapters.langchain_adapter import LangChainAdapter
    from langchain_openai import ChatOpenAI

    base_url, final_key = _resolve_llm_params(bp, api_key)

    llm = ChatOpenAI(model=bp.model, api_key=final_key, base_url=base_url)
    
    tools = bp.config.get("tools", [])
    if tools:
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{bp.description}\n\n{bp.instructions}"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        def to_dict_input(x):
            if isinstance(x, dict): return x
            return {"input": str(x)}
            
        def pick_output(x):
            return x.get("output", str(x))

        chain = RunnableLambda(to_dict_input) | agent_executor | RunnableLambda(pick_output)
        return LangChainAdapter(chain)

    template = ChatPromptTemplate.from_messages([
        ("system", f"{bp.description}\n\n{bp.instructions}"),
        ("user", "{input}")
    ])
    
    def to_dict_input(x):
        if isinstance(x, dict):
            return x
        return {"input": str(x)}

    chain = RunnableLambda(to_dict_input) | template | llm | StrOutputParser()
    
    return LangChainAdapter(chain)

def _create_langgraph_agent(bp: AgentConfig, api_key: str):
    from langgraph.graph import StateGraph, START, END
    from kibo_core.infrastructure.adapters.langgraph_adapter import LangGraphAdapter
    from typing import Annotated, TypedDict
    from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
    from langchain_openai import ChatOpenAI
    import operator

    base_url, final_key = _resolve_llm_params(bp, api_key)

    llm = ChatOpenAI(model=bp.model, api_key=final_key, base_url=base_url)

    class State(TypedDict):
        messages: Annotated[list[BaseMessage], operator.add]

    def chatbot(state: State):
        msgs = state["messages"]
        system_msg = SystemMessage(content=f"{bp.description}\n\n{bp.instructions}")
        response = llm.invoke([system_msg] + msgs)
        return {"messages": [response]}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    compiled_graph = graph_builder.compile()
    
    return LangGraphAdapter(compiled_graph)

def _create_mock_agent(bp: AgentConfig, api_key: str):
    import time
    from kibo_core.infrastructure.adapters.base import BaseAgentAdapter
    from kibo_core.domain.entities import AgentRequest, AgentResult

    class MockAdapter(BaseAgentAdapter):
        def __init__(self, duration: int):
            self.duration = duration
        
        def execute(self, request: AgentRequest) -> AgentResult:
            import platform
            import os
            time.sleep(self.duration)
            node = platform.node()
            pid = os.getpid()
            return AgentResult(
                output_data=f"Processed: {request.input_data}",
                metadata={"duration": self.duration, "node": node, "pid": pid}
            )

    duration = bp.config.get("duration", 1)
    return MockAdapter(duration)


def agent_factory(blueprint: AgentConfig, api_key: str = None):
    """
    Worker-side factory that instantiates the concrete agent.
    """
    engine = blueprint.agent.lower()
    
    if engine == "crewai":
        return _create_crewai_agent(blueprint, api_key)
    elif engine in ["agno", "phidata"]:
        return _create_agno_agent(blueprint, api_key)
    elif engine in ["pydantic_ai", "pydantic-ai"]: # Fix: Allow both underscore and hyphen
        return _create_pydantic_agent(blueprint, api_key)
    elif engine == "langchain":
        return _create_langchain_agent(blueprint, api_key)
    elif engine == "langgraph":
        return _create_langgraph_agent(blueprint, api_key)
    elif engine == "mock":
        return _create_mock_agent(blueprint, api_key)
    else:
        raise ValueError(f"Unsupported agent engine: {engine}")


def create_distributed_agent(blueprint: AgentConfig, api_key: str = None) -> LazyAgentAdapter:
    """
    Creates a LazyAgentAdapter ready for distributed execution from a Blueprint.
    """
    return LazyAgentAdapter(agent_factory, blueprint=blueprint, api_key=api_key)
