import os
import json
import time
import requests
from kibo_core import KiboAgent, AgentConfig

VIRTUAL_KEY = "sk-any-random-key"


def run_agent_with_budget():
    print(f"\n Acting as User using Key: {VIRTUAL_KEY}")
    print("   (Note: Persistent Budget tracking disabled because no DB is connected)")

    os.environ["KIBO_PROXY_URL"] = "http://localhost:4000"

    agent_config = AgentConfig(
        name="budget-agent",
        description="Cost-conscious assistant.",
        instructions="Say hello and tell me a very short joke about money.",
        framework="crewai",
        model="openai/gpt-4o-mini",
    )

    try:
        os.environ["OPENAI_API_KEY"] = VIRTUAL_KEY

        agent = KiboAgent(agent_config)
        result = agent.run("Do your job.")
        print(f"\nAgent Reply: {result.output_data}")

        print("\nRequest Cost Analysis (Stateless):")
        meta = result.metadata
        usage = meta.get("token_usage", {})
        print(f"   -> Model: {meta.get('model')}")
        print(f"   -> Usage: {usage}")

        if hasattr(usage, "prompt_tokens") and hasattr(usage, "completion_tokens"):
            cost = (
                usage.prompt_tokens * 0.15 + usage.completion_tokens * 0.60
            ) / 1_000_000
            print(f"   -> Approx Cost: ${cost:.6f}")

    except Exception as e:
        print(f"\n Execution Failed: {e}")
        return


if __name__ == "__main__":

    if not os.environ.get("OPENAI_API_KEY"):
        pass

    run_agent_with_budget()
