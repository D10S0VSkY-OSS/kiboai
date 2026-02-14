import sys
import os
from kibo_core import AgentConfig, create_agent


def main():
    print("--- LangChain + Ollama + Kibo Blueprint Example ---")

    agent_def = AgentConfig(
        name="Jester",
        description="A funny bot",
        instructions="Tell me a short joke about the topic provided by the user.",
        agent="langchain",
        model="ollama/llama3.1",
    )

    agent = create_agent(agent_def)

    print("Dispatching job to Kibo Cluster...")
    try:
        result = agent.run("software architects")

        print("\n--- Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure Ollama is running and accessible.")


if __name__ == "__main__":
    main()
