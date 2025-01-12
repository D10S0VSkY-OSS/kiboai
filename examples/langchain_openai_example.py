import sys
import os
from kibo_core import AgentConfig, create_agent


def main():
    print("--- LangChain + OpenAI + Kibo Blueprint Example ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    agent_def = AgentConfig(
        name="JesterAI",
        description="A funny bot backed by OpenAI",
        instructions="Tell me a short joke about the topic provided by the user.",
        agent="langchain",
        model="gpt-4o-mini",
    )

    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching job to Kibo Cluster...")
    try:
        result = agent.run("saving money")

        print("\n--- Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
