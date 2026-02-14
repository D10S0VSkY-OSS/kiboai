import os
from dotenv import load_dotenv
from kibo_core import AgentConfig, create_agent

# Import Native Agno Class
try:
    from agno.models.google import Gemini
except ImportError:
    print("Please install google-generativeai: pip install google-generativeai")
    exit(1)

load_dotenv()


def main():
    print("--- Agno Native Gemini Example ---")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set globally.")
        return

    # 1. Instantiate the Native Provider Object
    # This gives you full access to Agno's Google-specific features
    # (VertexAI params, safety settings, etc.) without Kibo filtering.
    native_model = Gemini(
        id="gemini-2.0-flash",  # Using 2.0 Flash as requested/compatible
        api_key=api_key,
        # You could add specific Google params here:
        # safety_settings={...}
    )

    # 2. Inject it into Kibo AgentConfig
    # Kibo factory will detect it's not a string and pass it through.
    agent_def = AgentConfig(
        name="AgnoGeminiUser",
        description="A native Gemini agent running on Agno.",
        instructions="Explain why passed native objects are better for advanced configuration.",
        agent="agno",
        model=native_model,  # <--- PASSING THE OBJECT directly
    )

    # 3. Create & Run
    agent = create_agent(agent_def)

    print("Running Agent...")
    result = agent.run("Hello Gemini!")
    print("\nResponse:")
    print(result.output_data)

    # Metadata check
    meta = result.metadata
    print(f"\nMetadata Usage Source: {type(meta.get('usage')).__name__}")


if __name__ == "__main__":
    main()
