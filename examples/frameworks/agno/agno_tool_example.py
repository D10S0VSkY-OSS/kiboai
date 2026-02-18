import os
import sys

# Ensure Kibo is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kiboai import AgentConfig, create_agent

try:
    from agno.tools.yfinance import YFinanceTools
except ImportError:
    print("Please install agno and yfinance: uv add agno yfinance")
    sys.exit(1)


def main():
    print("--- Agno (Phidata) Agent with Native Tool (YFinance) ---")

    # 1. Initialize Native Agno Tool
    # Agno (v1.x) includes all YFinance tools by default without boolean flags
    agno_tool = YFinanceTools()

    # 2. Configure Agent
    config = AgentConfig(
        name="StockAnalyst",
        description="A smart financial analyst running on Agno engine.",
        instructions="Use YFinance to find information about stocks.",
        agent="agno",
        config={
            # Agno specific configs
            "markdown": True,
            "tools": [agno_tool],  # Pass native tool directly
        },
    )

    # 3. Create & Run
    agent = create_agent(config, api_key="sk-dummy")

    try:
        # Prompt the agent
        result = agent.run("What is the current stock price of Apple (AAPL)?")
        print("\n--- Result ---")
        print(result.output_data)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
