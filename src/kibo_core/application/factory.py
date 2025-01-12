import os
from typing import Any, Callable
from kibo_core.domain.blueprint import AgentConfig
from kibo_core.infrastructure.adapters.base import LazyAgentAdapter
from crewai.llm import LLM

# --- Helper ---
def _resolve_llm_params(bp: AgentConfig, api_key: str):
    """
    Central logic to determine Model, Base URL and API Key.
    Prioritizes Kibo Proxy (LiteLLM) if configured, then Framework-specific defaults.
    """
    # 1. User config explicit overrides
    base_url = bp.config.get("base_url")
    final_api_key = api_key or bp.config.get("api_key")

    # 2. Check environment for Kibo Proxy (Default Gateway)
    # If user hasn't hardcoded a base_url, we check if we should map to the proxy
    if not base_url:
        proxy_url = os.getenv("KIBO_PROXY_URL") # e.g. http://localhost:4000
        if proxy_url:
            base_url = proxy_url
            if not final_api_key: final_api_key = "sk-kibo-proxy" # Dummy key for proxy
    
    # 3. If still no base_url and it's local ollama (legacy fallback)
    # This ensures examples run even without Proxy started if they target 'ollama/...'
    if not base_url and "ollama" in bp.model.lower() and "base_url" not in bp.config:
         # Some frameworks need explicit localhost:11434, others detect it. 
         # We'll leave it None so frameworks use their defaults, 
         # unless we implement specific logic per framework.
         pass

    return base_url, final_api_key

# --- Framework Factories ---

def _create_crewai_agent(bp: AgentConfig, api_key: str):
    from crewai import Agent, Task, Crew, Process
    from kibo_core.infrastructure.adapters.crewai_adapter import CrewAIAdapter
    
    base_url, final_key = _resolve_llm_params(bp, api_key)
    
    # CrewAI specific legacy fallback for Ollama if no proxy
    if not base_url and "ollama" in bp.model.lower():
         base_url = "http://localhost:11434"

    llm = LLM(model=bp.model, api_key=final_key, base_url=base_url)
    
    # CrewAI specific extras from config
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
    
    # For CrewAI, we typically need a Task wrapped in a Crew to run
    # Since Kibo execute() passes input, we create a generic Task placeholder
    # that will be interpolated with the input at runtime usually, 
    # but CrewAdapter kicksoff directly.
    
    # To make CrewAI compatible with a generic "run(input)" interface, 
    # we define a task that takes the input variable.
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
    
    base_url, final_key = _resolve_llm_params(bp, api_key)

    # Generic Model Selection via OpenAI Protocol (Works for Proxy & OpenAI)
    if base_url:
         from agno.models.openai import OpenAIChat
         # If using Proxy, commonly we pass model as is.
         model = OpenAIChat(id=bp.model, base_url=base_url, api_key=final_key)
    elif "ollama" in bp.model.lower():
         # Legacy direct Ollama
         from agno.models.ollama import Ollama
         model_id = bp.model.replace("ollama/", "")
         model = Ollama(id=model_id)
    else:
         from agno.models.openai import OpenAIChat
         model = OpenAIChat(id=bp.model, api_key=final_key)
    
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
    from kibo_core.infrastructure.adapters.pydantic_ai_adapter import PydanticAIAdapter
    
    base_url, final_key = _resolve_llm_params(bp, api_key)
    
    # Configure Environment for underlying OpenAI client if needed
    if final_key:
        os.environ["OPENAI_API_KEY"] = final_key
    
    model_arg = bp.model
    if base_url:
        os.environ["OPENAI_BASE_URL"] = base_url
        # If using proxy, ensure we use the OpenAI provider in PydanticAI
        if not model_arg.startswith("openai:") and not model_arg.startswith("ollama:"):
             model_arg = f"openai:{model_arg}"
    
    # PydanticAI uses system_prompt for description/instructions
    sys_prompt = f"{bp.description}\n\n{bp.instructions}"
    
    agent = Agent(
        model_arg, # e.g. 'openai:gpt-4o-mini' or 'ollama:llama3'
        system_prompt=sys_prompt
    )
    
    return PydanticAIAdapter(agent)

def _create_langchain_agent(bp: AgentConfig, api_key: str):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableLambda
    from kibo_core.infrastructure.adapters.langchain_adapter import LangChainAdapter

    base_url, final_key = _resolve_llm_params(bp, api_key)

    # Generic Model Selection
    if base_url:
        from langchain_openai import ChatOpenAI
        # Proxy usage: treat as OpenAI compatible
        llm = ChatOpenAI(model=bp.model, api_key=final_key, base_url=base_url)
    elif "ollama" in bp.model.lower() or "llama" in bp.model.lower():
        from langchain_ollama import OllamaLLM
        # Assuming model string is like 'llama3' or 'ollama/llama3'
        model_id = bp.model.replace("ollama/", "")
        llm = OllamaLLM(model=model_id)
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=bp.model, api_key=final_key)
    
    # Check for tools
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
        
        # Ensure input mapping and output selection
        def to_dict_input(x):
            if isinstance(x, dict): return x
            return {"input": str(x)}
            
        def pick_output(x):
            return x.get("output", str(x))

        # Wrap executor
        chain = RunnableLambda(to_dict_input) | agent_executor | RunnableLambda(pick_output)
        return LangChainAdapter(chain)

    # Generic Prompt Template
    template = ChatPromptTemplate.from_messages([
        ("system", f"{bp.description}\n\n{bp.instructions}"),
        ("user", "{input}")
    ])
    
    # Ensure input is mapped to "input" key if it's just a string, 
    # because ChatPromptTemplate typically expects a dict
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
    import operator

    base_url, final_key = _resolve_llm_params(bp, api_key)

    # Generic Model Selection
    if base_url:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=bp.model, api_key=final_key, base_url=base_url)
    elif "ollama" in bp.model.lower():
        from langchain_ollama import ChatOllama
        model_id = bp.model.replace("ollama/", "")
        llm = ChatOllama(model=model_id)
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=bp.model, api_key=final_key)

    # Define State
    class State(TypedDict):
        messages: Annotated[list[BaseMessage], operator.add]

    # Node function
    def chatbot(state: State):
        # Ensure system message is present (simple way)
        msgs = state["messages"]
        # In a real app we might manage history better, but for this factory:
        # Prepend system instruction if not present? 
        # Actually, let's just make sure the LLM knows the system prompt via wrapping or prepending.
        # Simplest is to invoke with system prompt + messages
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

    # Implement a quick internal adapter class
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

# --- Main Factory Dispatcher ---

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

# --- Kibo Public API ---

def create_distributed_agent(blueprint: AgentConfig, api_key: str = None) -> LazyAgentAdapter:
    """
    Creates a LazyAgentAdapter ready for distributed execution from a Blueprint.
    """
    return LazyAgentAdapter(agent_factory, blueprint=blueprint, api_key=api_key)
