import os
from typing import Annotated, TypedDict
import operator
from dotenv import load_dotenv
from kibo_core import AgentConfig, create_agent

# Import Native LangChain Google Class
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    print("Please install langchain-google-genai module.")
    exit(1)

load_dotenv()


def main():
    print("--- LangGraph Native Gemini Example ---")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set.")
        return

    # 1. Instantiate Native LangChain Model for use in LangGraph
    # LangGraph uses standard LangChain Chat Models
    native_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", google_api_key=api_key
    )

    # 2. Inject into Kibo
    # Kibo detects this is a LangGraph agent because of agent="langgraph".
    # Since we are passing a native LLM object, Kibo's factory will use it
    # to construct the default graph (Simple Chatbot) defined in _create_langgraph_agent.
    #
    # Note: Kibo's default LangGraph adapter builds a simple StateGraph.
    # Passing the native model overrides the default ChatOpenAI.
    agent_def = AgentConfig(
        name="LangGraphGeminiUser",
        description="A native Gemini agent running on LangGraph.",
        instructions="Explain concepts as a graph of thoughts.",
        agent="langgraph",  # <--- Important
        model=native_model,  # <--- PASSING THE OBJECT directly
    )

    # 3. Create & Run
    agent = create_agent(agent_def)

    print("Running LangGraph Agent...")
    # LangGraph usually returns a dict with 'messages', Kibo adapter extracts the last content
    result = agent.run("Hello Gemini!")
    print("\nResponse:")
    print(result.output_data)


if __name__ == "__main__":
    main()
