import os
from dotenv import load_dotenv
from kiboai import AgentConfig, create_agent

# Import Native CrewAI Class
try:
    from crewai import LLM
except ImportError:
    print("Please ensure crewai is installed.")
    exit(1)

load_dotenv()


def main():
    print("--- CrewAI Native Gemini Example ---")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set.")
        return

    # 1. Instantiate the Native CrewAI LLM Object
    # CrewAI uses LiteLLM syntax internally for the model string,
    # but wrapping it in LLM() allows passing specific config overrides.
    native_model = LLM(
        model="gemini/gemini-2.0-flash",  # CrewAI expects 'provider/model' format usually
        api_key=api_key,
        verbose=True,
    )

    # 2. Inject into Kibo
    agent_def = AgentConfig(
        name="CrewGeminiUser",
        description="A native Gemini agent running on CrewAI.",
        instructions="Explain the benefits of specific provider configurations.",
        agent="crewai",
        model=native_model,  # <--- PASSING THE OBJECT directly
        config={"verbose": True},
    )

    # 3. Create & Run
    agent = create_agent(agent_def)

    print("Running CrewAI Agent...")
    result = agent.run("Hello Gemini!")
    print("\nResponse:")
    print(result.output_data)


if __name__ == "__main__":
    main()
