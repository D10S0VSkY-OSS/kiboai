import asyncio
import os
import sys
from typing import Optional, Any, List
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kibo_core import AgentConfig, create_agent

PROXY_URL = os.getenv("KIBO_PROXY_URL", "http://localhost:4000")
MODEL_NAME = "openai/gpt-4o-mini"
TAVILY_KEY = os.getenv("TAVILY_API_KEY")

def get_agno_tool(api_key: str):
    """Returns Agno Tavily Tool or None if import fails."""
    if not api_key: return None
    try:
        from agno.tools.tavily import TavilyTools
        return TavilyTools(api_key=api_key)
    except ImportError:
        return None

def get_langchain_tool(api_key: str):
    """Returns LangChain Tavily Tool or Mock."""
    tool = None
    if api_key:
        try:
             from langchain_community.tools.tavily_search import TavilySearchResults
             tool = TavilySearchResults(api_key=api_key)
        except ImportError: pass
    
    if not tool:
        from langchain.tools import Tool
        return Tool(name="search", func=lambda x: "Mock Data: Market is stable.", description="Search mock")
    return tool

def get_crewai_tool(api_key: str):
    """Returns Custom CrewAI Tavily Tool or Mock."""
    tool = None
    if api_key:
        try:
            from crewai.tools import BaseTool
            from tavily import TavilyClient
            class TavilyCrewTool(BaseTool):
                name: str = "TavilySearch"
                description: str = "Search web."
                def _run(self, query: str) -> str:
                    return str(TavilyClient(api_key=api_key).search(query, search_depth="basic"))
            tool = TavilyCrewTool()
        except ImportError: pass

    if not tool:
        try:
            from crewai.tools import BaseTool
            class MockTool(BaseTool):
                name: str="Search"
                description: str="Mock search"
                def _run(self, q: str) -> str: return "Mock Data: Stocks up."
            return MockTool()
        except ImportError: return None
    return tool

def make_agent(name: str, task: str, engine: str, tools: Optional[List[Any]] = None) -> Any:
    """Simplified agent creation wrapper."""
    
    tools = [] if tools is None else list(tools)

    config_params = {
        "base_url": PROXY_URL, 
        "temperature": 0.0,  # Deterministic output
        "tools": list(filter(None, tools)) # Remove Nones
    }
    
    return create_agent(AgentConfig(
        name=name,
        description=f"Specialist agent for {name}",
        instructions=task,
        agent=engine,
        model=MODEL_NAME,
        config=config_params
    ), api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"))

def get_cost(res: Any) -> float:
    """Extracts cost from result metadata."""
    if not res or isinstance(res, Exception): return 0.0
    
    if res.metadata.get("cost") is not None:
        return float(res.metadata["cost"])

    usage = res.metadata.get("token_usage") or res.metadata.get("usage", {})
    
    if hasattr(usage, "request_tokens"):
        usage = {"prompt_tokens": usage.request_tokens, "completion_tokens": usage.response_tokens}
    elif hasattr(usage, "input_tokens"):
        usage = {"prompt_tokens": usage.input_tokens, "completion_tokens": usage.output_tokens, "cost": getattr(usage, "cost", None)}
    elif hasattr(usage, "__dict__"):
        usage = usage.__dict__

    if usage.get("response_cost") is not None:
        return float(usage["response_cost"])
    if usage.get("cost") is not None:
        return float(usage["cost"])

    p = usage.get("prompt_tokens", 0)
    c = usage.get("completion_tokens", 0)
    return (p * 0.15 + c * 0.60) / 1_000_000

async def main():
    print(f" Starting Kibo Workflow [Model: {MODEL_NAME}]")
    if not TAVILY_KEY: print(" Running in MOCK mode (No TAVILY_API_KEY)")

    agents = [
        make_agent("GoldAgent", "Find current Gold/XAU price (USD).", "agno", [get_agno_tool(TAVILY_KEY)]),
        make_agent("CryptoAgent", "Summarize top Blockchain news.", "langchain", [get_langchain_tool(TAVILY_KEY)]),
        make_agent("StockAgent", "Get prices: NVDA, MSFT, GOOG.", "crewai", [get_crewai_tool(TAVILY_KEY)])
    ]
    
    print("\n Launching parallel tasks...")
    prompts = [
        "Price of Gold today?", 
        "Blockchain news summary.", 
        "Stock prices for NVDA, MSFT, GOOG."
    ]
    
    futures = [agent.run_async(p) for agent, p in zip(agents, prompts)]
    
    results = await asyncio.gather(*[asyncio.to_thread(f.result) for f in futures], return_exceptions=True)

    context = ""
    total_cost = 0.0
    
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            print(f" Task {i+1} failed: {res}")
            continue

        cost = get_cost(res)
        total_cost += cost
        src = res.metadata.get('adapter', 'Unknown')
        print(f" {src} done (${cost:.6f})")
        context += f"\n--- {src} Report ---\n{res.output_data}\n"

    print("\n Synthesizing advice...")
    advisor = make_agent(
        "Advisor", 
        "Analyze reports. Suggest portfolio allocation (Stocks/Crypto/Gold). Explain why.", 
        "pydantic_ai"
    )
    
    final = advisor.run(f"Market Data:\n{context}")
    
    cost_adv = get_cost(final)
    total_cost += cost_adv
    
    print("\n=== FINAL STRATEGY ===")
    print(final.output_data)
    print(f"\n💵 Total Cost: ${total_cost:.6f}")

if __name__ == "__main__":
    asyncio.run(main())
