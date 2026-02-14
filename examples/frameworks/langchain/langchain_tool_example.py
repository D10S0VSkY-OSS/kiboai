import os
import sys

# Ensure Kibo is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kibo_core import AgentConfig, create_agent

# Set a dummy key to avoid init errors if the user hasn't set it yet
if "SERPER_API_KEY" not in os.environ:
    print(
        "Notice: SERPER_API_KEY not found. Using a placeholder. Execution will fail unless set."
    )
    os.environ["SERPER_API_KEY"] = "sk-placeholder"

try:
    from langchain_community.utilities import GoogleSerperAPIWrapper
    from langchain_core.tools import Tool
except ImportError:
    print("Please install langchain-community: uv add langchain-community")
    sys.exit(1)


def main():
    print("--- LangChain Agent with Native Tool (Google Serper) ---")

    # 1. Initialize Native LangChain Tool
    # Custom wrapper around Google Serper API
    search = GoogleSerperAPIWrapper()

    # Wrap in a standard Tool for the agent
    serper_tool = Tool(
        name="google_serper",
        description="A search engine. Useful for when you need to answer questions about current events. Input should be a search query.",
        func=search.run,
    )

    # 2. Configure Agent
    config = AgentConfig(
        name="LangChainResearcher",
        description="An internet researcher powered by LangChain.",
        instructions="Search for 'Kibo AI framework' using Google Serper and summarize results.",
        agent="langchain",
        config={"verbose": True, "tools": [serper_tool]},  # Pass native tool directly
    )

    # 3. Create & Run
    agent = create_agent(config, api_key="sk-dummy")

    try:
        result = agent.run("What is Kibo AI?")
        print("\n--- Result ---")
        print(result.output_data)
    except Exception as e:
        print(f"Error executing agent: {e}")


if __name__ == "__main__":
    main()
