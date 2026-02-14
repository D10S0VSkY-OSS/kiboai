import asyncio
import os
import sys
from typing import Optional, Any, List
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kibo_core import AgentConfig, create_agent
from kibo_core.infrastructure.tools import TavilySearchTool

PROXY_URL = os.getenv("KIBO_PROXY_URL", "http://localhost:4000")
MODEL_NAME = "openai/gpt-4o-mini"
TAVILY_KEY = os.getenv("TAVILY_API_KEY")


def make_agent(
    name: str, task: str, engine: str, tools: Optional[List[Any]] = None
) -> Any:
    """Simplified agent creation wrapper."""

    tools = [] if tools is None else list(tools)

    config_params = {
        "base_url": PROXY_URL,
        "temperature": 0.0,  # Deterministic output
        "tools": list(filter(None, tools)),  # Remove Nones
    }

    return create_agent(
        AgentConfig(
            name=name,
            description=f"Specialist agent for {name}",
            instructions=task,
            agent=engine,
            model=MODEL_NAME,
            config=config_params,
        ),
        api_key=os.getenv("OPENAI_API_KEY", "sk-dummy"),
    )


def get_cost(res: Any) -> float:
    """Extracts cost from result metadata."""
    if not res or isinstance(res, Exception):
        return 0.0

    if res.metadata.get("cost") is not None:
        return float(res.metadata["cost"])

    usage = res.metadata.get("token_usage") or res.metadata.get("usage", {})

    if hasattr(usage, "request_tokens"):
        usage = {
            "prompt_tokens": usage.request_tokens,
            "completion_tokens": usage.response_tokens,
        }
    elif hasattr(usage, "input_tokens"):
        usage = {
            "prompt_tokens": usage.input_tokens,
            "completion_tokens": usage.output_tokens,
            "cost": getattr(usage, "cost", None),
        }
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
    if not TAVILY_KEY:
        print(" Running in MOCK mode (No TAVILY_API_KEY)")

    # Universal Kibo Tool
    tavily_tool = TavilySearchTool(api_key=TAVILY_KEY)

    agents = [
        make_agent(
            "GoldAgent",
            "Find current Gold/XAU price (USD).",
            "agno",
            [tavily_tool],
        ),
        make_agent(
            "CryptoAgent",
            "Summarize top Blockchain news.",
            "langchain",
            [tavily_tool],
        ),
        make_agent(
            "StockAgent",
            "Get prices: NVDA, MSFT, GOOG.",
            "crewai",
            [tavily_tool],
        ),
    ]

    print("\n Launching parallel tasks...")
    prompts = [
        "Price of Gold today?",
        "Blockchain news summary.",
        "Stock prices for NVDA, MSFT, GOOG.",
    ]

    futures = [agent.run_async(p) for agent, p in zip(agents, prompts)]

    results = await asyncio.gather(
        *[asyncio.to_thread(f.result) for f in futures], return_exceptions=True
    )

    context = ""
    total_cost = 0.0

    for i, res in enumerate(results):
        if isinstance(res, Exception):
            print(f" Task {i+1} failed: {res}")
            continue

        cost = get_cost(res)
        total_cost += cost
        src = res.metadata.get("adapter", "Unknown")
        print(f" {src} done (${cost:.6f})")
        context += f"\n--- {src} Report ---\n{res.output_data}\n"

    print("\n Synthesizing advice...")
    advisor = make_agent(
        "Advisor",
        "Analyze reports. Suggest portfolio allocation (Stocks/Crypto/Gold). Explain why.",
        "pydantic_ai",
    )

    final = advisor.run(f"Market Data:\n{context}")

    cost_adv = get_cost(final)
    total_cost += cost_adv

    print("\n=== FINAL STRATEGY ===")
    print(final.output_data)
    print(f"\n💵 Total Cost: ${total_cost:.6f}")


if __name__ == "__main__":
    asyncio.run(main())
