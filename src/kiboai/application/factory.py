import os
from typing import Any, Callable, Optional
from kiboai.domain.blueprint import AgentConfig
from kiboai.infrastructure.adapters.base import LazyAgentAdapter
from kiboai.application.converters import convert_tools
from kiboai.infrastructure.a2a.config import A2AConfig

# Lazy imports moved to usage sites
# from crewai.llm import LLM
# from kiboai.infrastructure.a2a.adapter import ...

from kiboai.infrastructure.observability.langfuse import (
    LangfuseTracingAdapter,
    normalize_langfuse_config,
)


def _resolve_llm_params(bp: AgentConfig, api_key: str):
    """
    Central logic to determine Model, Base URL and API Key.
    Prioritizes Kibo Proxy (LiteLLM) if configured, then Framework-specific defaults.
    """
    base_url = bp.config.get("base_url")
    final_api_key = api_key or bp.config.get("api_key")

    if not base_url:
        proxy_url = os.getenv("KIBO_PROXY_URL")  # e.g. http://localhost:4000
        if proxy_url:
            base_url = proxy_url
            if not final_api_key:
                final_api_key = "sk-kibo-proxy"  # Dummy key for proxy

    return base_url, final_api_key


def _normalize_a2a_config(value: Any) -> Optional[A2AConfig]:
    if isinstance(value, A2AConfig):
        return value
    if isinstance(value, dict):
        return A2AConfig(**value)
    return None


def _build_agno_model(bp: AgentConfig, api_key: str):
    from agno.models.openai import OpenAIChat
    from agno.models.litellm import LiteLLM

    if not isinstance(bp.model, str):
        return bp.model

    base_url, final_key = _resolve_llm_params(bp, api_key)
    if base_url:
        return OpenAIChat(id=bp.model, base_url=base_url, api_key=final_key)
    return LiteLLM(id=bp.model)


def _build_agno_agent_instance(bp: AgentConfig, api_key: str):
    from agno.agent import Agent

    model = _build_agno_model(bp, api_key)
    agent_config = bp.config.copy()

    a2a_config = _normalize_a2a_config(getattr(bp, "a2a", None))
    if a2a_config and a2a_config.agent_id and "id" not in agent_config:
        agent_config["id"] = a2a_config.agent_id

    markdown = agent_config.pop("markdown", True)
    tools = agent_config.pop("tools", [])

    agent_config.pop("base_url", None)
    agent_config.pop("api_key", None)
    agent_config.pop("temperature", None)

    final_tools = convert_tools(tools, "agno")

    return Agent(
        name=bp.name,
        model=model,
        description=bp.description,
        instructions=bp.instructions,
        markdown=markdown,
        tools=final_tools,
        **agent_config,
    )


def _create_crewai_agent(bp: AgentConfig, api_key: str):
    from crewai import Agent, Task, Crew, Process
    from crewai.llm import LLM
    from kiboai.infrastructure.adapters.crewai_adapter import CrewAIAdapter

    if not isinstance(bp.model, str):
        llm = bp.model
    else:
        base_url, final_key = _resolve_llm_params(bp, api_key)
        llm = LLM(model=bp.model, api_key=final_key, base_url=base_url)

    agent_config = bp.config.copy()

    verbose = agent_config.pop("verbose", True)
    allow_delegation = agent_config.pop("allow_delegation", False)
    tools = agent_config.pop("tools", [])

    agent_config.pop("base_url", None)
    agent_config.pop("api_key", None)

    final_tools = convert_tools(tools, "crewai")

    researcher = Agent(
        role=bp.name,
        goal=bp.instructions,
        backstory=bp.description,
        verbose=verbose,
        allow_delegation=allow_delegation,
        llm=llm,
        tools=final_tools,
        **agent_config,  # Pass remaining config as kwargs
    )

    task = Task(
        description=f"Parse the following input and Execute instructions: {bp.instructions}. \nInput: {{topic}}",
        agent=researcher,
        expected_output="Result of the instructions.",
    )

    crew = Crew(
        agents=[researcher], tasks=[task], verbose=verbose, process=Process.sequential
    )

    return CrewAIAdapter(crew)


def _create_agno_agent(bp: AgentConfig, api_key: str):
    from kiboai.infrastructure.adapters.agno_adapter import AgnoAdapter

    agent = _build_agno_agent_instance(bp, api_key)

    return AgnoAdapter(agent)


def _create_pydantic_agent(bp: AgentConfig, api_key: str):
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider
    from kiboai.infrastructure.adapters.pydantic_ai_adapter import PydanticAIAdapter
    from kiboai.shared_kernel.logging import logger

    if not isinstance(bp.model, str):
        model = bp.model
    else:
        base_url, final_key = _resolve_llm_params(bp, api_key)

        model_arg = bp.model
        if model_arg.startswith("openai:") and base_url:
            model_arg = model_arg.replace("openai:", "")
            provider = OpenAIProvider(base_url=base_url, api_key=final_key)
            model = OpenAIModel(model_arg, provider=provider)
        elif base_url:
            provider = OpenAIProvider(base_url=base_url, api_key=final_key)
            model = OpenAIModel(model_arg, provider=provider)
        else:
            model = model_arg

    # 1. Native Object Mode: Pass-through if model is not a string
    if not isinstance(bp.model, str):
        model = bp.model
    else:
        # 2. String Mode: Proxy or Known Providers
        base_url, final_key = _resolve_llm_params(bp, api_key)

        model_arg = bp.model
        if model_arg.startswith("openai:") and base_url:
            # Force proxy usage for OpenAI-like models if enabled
            model_arg = model_arg.replace("openai:", "")
            provider = OpenAIProvider(base_url=base_url, api_key=final_key)
            model = OpenAIModel(model_arg, provider=provider)
        elif base_url:
            # If Proxy is active, force OpenAI protocol regardless of prefix
            provider = OpenAIProvider(base_url=base_url, api_key=final_key)
            model = OpenAIModel(model_arg, provider=provider)
        else:
            # 3. Universal Mode (No Proxy): PydanticAI resolves string automatically (OpenAI, Gemini, etc)
            # We pass the string directly to Agent, which resolves it.
            # However, logic below expects 'model' object.
            # We can let PydanticAI resolve the string if we pass it as string.
            # But we need to handle the case where it's passed to Agent constructor.
            # Current Implementation assumed 'model' var is an automated object.
            # Let's stringify it if we can.
            model = model_arg

    # Define system prompt from blueprint
    sys_prompt = f"{bp.description}\n\n{bp.instructions}"

    agent_config = bp.config.copy()
    agent_config.pop("base_url", None)
    agent_config.pop("api_key", None)
    tools = agent_config.pop("tools", [])

    final_tools = convert_tools(tools, "pydantic_ai")

    agent = Agent(
        model,
        system_prompt=sys_prompt,
    )

    import inspect
    from pydantic_ai import RunContext

    for t in final_tools:
        sig = inspect.signature(t)
        params = list(sig.parameters.values())
        is_context_aware = False
        if params:
            first_param = params[0]
            if first_param.annotation != inspect.Parameter.empty:
                logger.info(
                    f"Checking tool {t.__name__} param {first_param.name} type: {first_param.annotation}"
                )
                if "RunContext" in str(first_param.annotation):
                    is_context_aware = True

        if is_context_aware:
            agent.tool(t)
        else:
            agent.tool_plain(t)

    return PydanticAIAdapter(agent)


def _create_langchain_agent(bp: AgentConfig, api_key: str):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableLambda
    from kiboai.infrastructure.adapters.langchain_adapter import LangChainAdapter
    from langchain_openai import ChatOpenAI

    if not isinstance(bp.model, str):
        llm = bp.model
    else:
        base_url, final_key = _resolve_llm_params(bp, api_key)

        if base_url:
            llm = ChatOpenAI(model=bp.model, api_key=final_key, base_url=base_url)
        else:
            try:
                from langchain_community.chat_models import ChatLiteLLM

                llm = ChatLiteLLM(model=bp.model)
            except ImportError:
                if not final_key:
                    error_msg = (
                        f"❌ Configuration Error: Cannot instantiate ChatOpenAI for model '{bp.model}' because "
                        "the 'final_key' (API Key) is missing. Please ensure langchain-community is installed "
                        "for broad model support, or provide a valid API key for direct OpenAI usage."
                    )
                    print(error_msg)
                    raise ValueError(error_msg)

                llm = ChatOpenAI(model=bp.model, api_key=final_key)

    tools = bp.config.get("tools", [])
    if tools:
        final_tools = convert_tools(tools, "langchain")

        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", f"{bp.description}\n\n{bp.instructions}"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(llm, final_tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=final_tools, verbose=True)

        def to_dict_input(x):
            if isinstance(x, dict):
                return x
            return {"input": str(x)}

        def pick_output(x):
            return x.get("output", str(x))

        chain = (
            RunnableLambda(to_dict_input) | agent_executor | RunnableLambda(pick_output)
        )
        return LangChainAdapter(chain)

    template = ChatPromptTemplate.from_messages(
        [("system", f"{bp.description}\n\n{bp.instructions}"), ("user", "{input}")]
    )

    def to_dict_input(x):
        if isinstance(x, dict):
            return x
        return {"input": str(x)}

    chain = RunnableLambda(to_dict_input) | template | llm | StrOutputParser()

    return LangChainAdapter(chain)


def _create_langgraph_agent(bp: AgentConfig, api_key: str):
    from langgraph.graph import StateGraph, START, END
    from kiboai.infrastructure.adapters.langgraph_adapter import LangGraphAdapter
    from typing import Annotated, TypedDict
    from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
    from langchain_openai import ChatOpenAI
    import operator

    if not isinstance(bp.model, str):
        llm = bp.model
    else:
        base_url, final_key = _resolve_llm_params(bp, api_key)

        if base_url:
            llm = ChatOpenAI(model=bp.model, api_key=final_key, base_url=base_url)
        else:
            try:
                from langchain_community.chat_models import ChatLiteLLM

                llm = ChatLiteLLM(model=bp.model)
            except ImportError:
                if not final_key:
                    raise ValueError(
                        f"❌ Configuration Error: Cannot instantiate ChatOpenAI for model '{bp.model}' because "
                        "the 'final_key' (API Key) is missing. Please ensure langchain-community is installed "
                        "for broad model support, or provide a valid API key for direct OpenAI usage."
                    )
                llm = ChatOpenAI(model=bp.model, api_key=final_key)

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
    from kiboai.infrastructure.adapters.base import BaseAgentAdapter
    from kiboai.domain.entities import AgentRequest, AgentResult

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
                metadata={"duration": self.duration, "node": node, "pid": pid},
            )

    duration = bp.config.get("duration", 1)
    return MockAdapter(duration)


def agent_factory(blueprint: AgentConfig, api_key: str = None):
    """
    Worker-side factory that instantiates the concrete agent.
    """
    a2a_config = _normalize_a2a_config(getattr(blueprint, "a2a", None))
    engine = blueprint.agent.lower()
    if a2a_config and a2a_config.enabled and engine in ["agno", "phidata"]:
        from kiboai.infrastructure.a2a.adapter import (
            AgnoA2AClientAdapter,
            AgnoA2AServerAdapter,
        )

        if a2a_config.mode == "client":
            return AgnoA2AClientAdapter(a2a_config.resolved_base_url())
        if a2a_config.mode == "server":
            agno_agent = _build_agno_agent_instance(blueprint, api_key)
            return AgnoA2AServerAdapter(
                agno_agent,
                host=a2a_config.host,
                port=a2a_config.port,
                agent_id=a2a_config.agent_id,
                access_log=a2a_config.access_log,
            )

    if engine == "crewai":
        return _create_crewai_agent(blueprint, api_key)
    elif engine in ["agno", "phidata"]:
        return _create_agno_agent(blueprint, api_key)
    elif engine in [
        "pydantic_ai",
        "pydantic-ai",
    ]:  # Fix: Allow both underscore and hyphen
        return _create_pydantic_agent(blueprint, api_key)
    elif engine == "langchain":
        return _create_langchain_agent(blueprint, api_key)
    elif engine == "langgraph":
        return _create_langgraph_agent(blueprint, api_key)
    elif engine == "mock":
        return _create_mock_agent(blueprint, api_key)
    else:
        raise ValueError(f"Unsupported agent engine: {engine}")


def create_distributed_agent(
    blueprint: AgentConfig, api_key: str = None
) -> LazyAgentAdapter:
    """
    Creates a LazyAgentAdapter ready for distributed execution from a Blueprint.
    """
    adapter = LazyAgentAdapter(agent_factory, blueprint=blueprint, api_key=api_key)
    langfuse_config = normalize_langfuse_config(getattr(blueprint, "langfuse", None))
    if langfuse_config and langfuse_config.enabled:
        return LangfuseTracingAdapter(
            adapter, langfuse_config, agent_name=blueprint.name
        )
    return adapter
