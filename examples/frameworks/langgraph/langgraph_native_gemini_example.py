import os
from typing import Annotated, Dict, List, TypedDict, Union
import operator
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    print("Please install langchain-google-genai module.")
    exit(1)

from kiboai import AgentConfig, KiboAgent
from kiboai.domain.graph import KiboGraph, START, END
from kiboai.infrastructure.graph_compiler import compile_graph

# Load environment variables
load_dotenv()


class AgentState(TypedDict):
    """
    State definition for the multi-step graph.
    """

    messages: Annotated[List[BaseMessage], operator.add]
    topic: str


def main():
    print("--- Kibo Native Graph Example (Gemini) ---")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set.")
        return

    # 1. Instantiate Native LangChain Model for use in LangGraph nodes
    # We use the same model instance for all agents to keep it simple,
    # but you could instantiate different models (e.g. gemini-pro vs gemini-flash)
    native_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", google_api_key=api_key
    )

    # 2. Define Kibo Agents (The "Nodes")
    # We use 'agent="langchain"' to leverage the native LangChain integration
    # which accepts the ChatGoogleGenerativeAI object directly.
    # Note: In a declarative setup, the model object is passed to each node definition.

    writer = AgentConfig(
        name="GeminiWriter",
        description="Write a draft about the topic.",
        instructions="You are a technical writer. Write a short explanation about the requested topic using Gemini.",
        agent="langchain",  # Explicitly use langchain adapter which handles LangChain models
        model=native_model,  # Pass the object directly
    )

    reviewer = AgentConfig(
        name="GeminiReviewer",
        description="Critique the draft.",
        instructions="You are an editor. Review the previous text critically in 1 sentence.",
        agent="langchain",
        model=native_model,
    )

    finalizer = AgentConfig(
        name="GeminiPublisher",
        description="Finalize the text.",
        instructions="Improve the draft based on the critique provided in the conversation history.",
        agent="langchain",
        model=native_model,
    )

    # 3. Define the Graph Structure Declaratively
    graph = KiboGraph(
        name="GeminiContentPipeline", state_schema=AgentState, entry_point="writer"
    )

    # Add Nodes (Agents)
    graph.add_node("writer", agent=writer)
    graph.add_node("reviewer", agent=reviewer)
    graph.add_node("finalizer", agent=finalizer)

    # Add Edges (Flow)
    # Sequential: Writer -> Reviewer -> Finalizer -> End
    graph.add_edge(START, "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", "finalizer")
    graph.add_edge("finalizer", END)

    # 4. Compile & Run
    print("Compiling KiboGraph to LangGraph adapter...")
    # Note: verify validation of key or config passed to compile_graph if needed
    # But here we already injected the model with key into the agents.
    adapter = compile_graph(graph, api_key=api_key)

    # Wrap the adapter in a KiboAgent to use the standardized execution interface
    kibo_agent = KiboAgent(
        config=AgentConfig(
            name="GeminiContentPipelineGraph",
            description="Orchestrates the writing process with Gemini.",
            instructions="Execute the graph workflow.",
            agent="langgraph",
            model="mixed",  # Placeholder
        ),
        adapter=adapter,
    )

    print("Dispatching task via Kibo Graph (Gemini)...")
    try:
        # Input matching our State definition
        # Manually constructing the initial state
        initial_message = HumanMessage(content="Explain Quantum Computing")
        input_data = {"messages": [initial_message], "topic": "Quantum Computing"}

        # execution
        result = kibo_agent.run(input_data)

        # Result output might be the full state or the last message depending on adapter
        # The LangChain/Graph adapter usually returns the final state dict.
        print("\n--- Result ---")
        if isinstance(result.output_data, dict) and "messages" in result.output_data:
            print("Conversation History:")
            for msg in result.output_data["messages"]:
                # Simple type check for display
                prefix = "User" if isinstance(msg, HumanMessage) else "AI"
                # If msg is a dict (sometimes happens in serialization), handle it
                content = msg.content if hasattr(msg, "content") else str(msg)
                print(
                    f"{prefix}: {content[:100]}..."
                    if len(content) > 100
                    else f"{prefix}: {content}"
                )
        else:
            print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
