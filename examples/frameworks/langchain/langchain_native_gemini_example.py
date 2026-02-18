import os
from dotenv import load_dotenv
from kiboai import AgentConfig, create_agent

# Import Native LangChain Google Class
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    print("Please install langchain-google-genai module.")
    exit(1)

load_dotenv()


def main():
    print("--- LangChain Native Gemini Example ---")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set.")
        return

    # 1. Instantiate Native LangChain Model
    # This gives access to top_p, top_k, and other Google-specific params
    native_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True,  # Known fix for some Gemini versions
    )

    # 2. Inject into Kibo
    agent_def = AgentConfig(
        name="LangChainGeminiUser",
        description="A native Gemini agent running on LangChain.",
        instructions="Say hello.",
        agent="langchain",
        model=native_model,  # <--- PASSING THE OBJECT directly
    )

    # 3. Create & Run
    agent = create_agent(agent_def)

    print("Running LangChain Agent...")
    result = agent.run("Hello Gemini!")
    print("\nResponse:")
    print(result.output_data)


if __name__ == "__main__":
    main()
