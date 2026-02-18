import sys
import os
from kiboai import AgentConfig, create_agent


def main():
    print("--- CrewAI + Ollama + Kibo Blueprint Example ---")

    agent_def = AgentConfig(
        name="Researcher",
        description="An AI researcher obsessed with agents.",
        instructions="Discover new AI trends",
        agent="crewai",
        model="ollama/llama3.1",
        config={"verbose": True, "allow_delegation": False},
    )

    agent = create_agent(agent_def)

    print("Dispatching Crew to Kibo Cluster...")
    try:
        result = agent.run("Distributed AI Agents")

        print("\n--- Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure Ollama is running and accessible (ollama serve).")


if __name__ == "__main__":
    main()
