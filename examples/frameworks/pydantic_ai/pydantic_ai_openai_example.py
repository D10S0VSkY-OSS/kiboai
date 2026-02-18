import os
from kiboai import AgentConfig, create_agent


def main():
    print("--- PydanticAI + OpenAI + Kibo Blueprint Example ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        return

    agent_def = AgentConfig(
        name="GeneralBot",
        description="A general purpose assistant",
        instructions="You are a helpful assistant.",
        agent="pydantic-ai",
        model="gpt-4o-mini",
    )

    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching task...")
    try:
        result = agent.run("What is the capital of France?")

        print("\nResult:")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
