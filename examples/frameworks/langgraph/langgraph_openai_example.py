import os
from typing import Annotated, Dict, List, TypedDict, Union
import operator
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage

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
    print("--- Kibo Native Graph Example (Declarative) ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set.")
        return

    # 1. Define Kibo Agents (The "Nodes")
    # These are pure config objects - execution engine is decided later
    writer = AgentConfig(
        name="TechWriter",
        description="Write a draft about the topic.",
        instructions="You are a technical writer. Write a short explanation about the requested topic.",
        model="gpt-4o-mini",
        config={"temperature": 0.7},
    )

    reviewer = AgentConfig(
        name="Editor",
        description="Critique the draft.",
        instructions="You are an editor. Review the previous text critically in 1 sentence.",
        model="gpt-4o-mini",
        config={"temperature": 0.0},
    )

    finalizer = AgentConfig(
        name="Publisher",
        description="Finalize the text.",
        instructions="Improve the draft based on the critique provided in the conversation history.",
        model="gpt-4o-mini",
        config={"temperature": 0.5},
    )

    # 2. Define the Graph Structure Declaratively
    # 'KiboGraph' abstracts away the underlying StateGraph
    graph = KiboGraph(
        name="ContentPipeline", state_schema=AgentState, entry_point="writer"
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

    # 3. Compile & Run
    # Kibo compiles this to a runnable app (currently using LangGraph as backend)
    # In the future, this could compile to a pure Ray DAG without LangGraph if needed.
    print("Compiling KiboGraph to LangGraph adapter...")
    adapter = compile_graph(graph, api_key=api_key)

    # Wrap the adapter in a KiboAgent to use the standardized execution interface
    # This allows us to run it locally or distributed (via Ray)
    kibo_agent = KiboAgent(
        config=AgentConfig(
            name="ContentPipelineGraph",
            description="Orchestrates the writing process.",
            instructions="Execute the graph workflow.",
            agent="langgraph",
            model="mixed",
        ),
        adapter=adapter,
    )

    print("Dispatching task via Kibo Graph...")
    try:
        # Input matching our State definition
        # Kibo's compiler wrapper automatically handles passing this inputs to the first agent
        input_data = {"messages": [HumanMessage(content="Event Driven Architecture")]}

        # app is a LangGraphAdapter instance, which we can treat as a "Super Agent"
        result = kibo_agent.run(input_data)

        print("\n--- Final Result ---")
        print(f"Output: {result.output_data}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
