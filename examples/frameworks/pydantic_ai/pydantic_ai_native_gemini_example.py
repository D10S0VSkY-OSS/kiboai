import os
from dotenv import load_dotenv
from kibo_core import AgentConfig, create_agent

# Import Native PydanticAI Google Class
try:
    from pydantic_ai.models.gemini import GeminiModel
except ImportError:
    print("Please install pydantic-ai[google] or similar.")
    exit(1)

load_dotenv()


def main():
    print("--- PydanticAI Native Gemini Example ---")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set.")
        return

    # PydanticAI Gemini Provider specifically looks for GEMINI_API_KEY
    # We map our standard GOOGLE_API_KEY to satisfy it without changing .env
    os.environ["GEMINI_API_KEY"] = api_key

    # 1. Instantiate Native PydanticAI Model
    # GeminiModel automatically reads GEMINI_API_KEY from environment variables
    native_model = GeminiModel("gemini-2.0-flash")

    # 2. Inject into Kibo
    agent_def = AgentConfig(
        name="PydanticGeminiUser",
        description="A native Gemini agent running on PydanticAI.",
        instructions="Say hello.",
        agent="pydantic-ai",
        model=native_model,  # <--- PASSING THE OBJECT directly
    )

    # 3. Create & Run
    agent = create_agent(agent_def)

    print("Running PydanticAI Agent...")
    result = agent.run("Hello Gemini!")
    print("\nResponse:")
    print(result.output_data)


if __name__ == "__main__":
    main()
