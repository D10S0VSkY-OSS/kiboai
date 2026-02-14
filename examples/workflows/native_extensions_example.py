import os
from typing import TypedDict, Annotated, List
import operator
from dotenv import load_dotenv

from kibo_core.domain.blueprint import AgentConfig
from kibo_core.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kibo_core import create_workflow, KiboAgent
from langchain_core.messages import HumanMessage, BaseMessage

# Load environment variables
load_dotenv()


def main():
    print("--- Declarative Workflow with Native Extensions (LangGraph) ---")

    api_key = os.getenv("OPENAI_API_KEY")

    writer_agent = AgentConfig(
        name="TechWriter",
        description="Writer",
        instructions="Write a short sentence about the topic.",
        model="gpt-4o-mini",
    )

    # --- Strategy 1 & 2 Demo ---

    # 1. Prepare Native Object (MemorySaver for checkpointer)
    # This comes from langgraph, Kibo doesn't natively expose it but supports passing it.
    from langgraph.checkpoint.memory import MemorySaver

    memory = MemorySaver()

    # 2. Define a Hook function
    # This function receives the native StateGraph builder
    def custom_graph_modifier(graph_builder):
        print(">> [Hook] Executing custom native logic on graph builder...")
        # We can inspect or modify the builder using native LangGraph API
        # E.g. Add a node dynamically or change an edge (just logging here)
        print(f">> [Hook] Current nodes: {graph_builder.nodes.keys()}")

    # 3. Define Workflow with overrides
    workflow_def = WorkflowConfig(
        name="MemoryPipeline",
        description="Pipeline with memory",
        engine="langgraph",
        start_step="step1",
        steps=[
            WorkflowStep(
                id="step1",
                agent=writer_agent,
                instruction="Write about: {input}",
                next=None,
            )
        ],
        # Pass native extensions (Strategy 1)
        native_extensions={
            "checkpointer": memory,
            # "interrupt_before": ["step1"] # Example of other native param
        },
        # Pass hook (Strategy 2)
        on_before_compile=custom_graph_modifier,
    )

    print(f"Compiling workflow with extensions...")

    adapter = create_workflow(workflow_def, api_key=api_key)

    # To use checkpointer, we need thread_id in config
    # Kibo passes request.context.params as config to execution.

    # Manual execution to simulate stateful interaction?
    # Actually KiboAgent handles the Adapter, but passing thread_id via run()
    # requires KiboAgent support for extra params or passing them in input structure if adapter allows.
    # The current LangChainAdapter uses `request.context.params` for runnable config.
    # We sadly cannot easily pass thread_id via standard KiboAgent.run(input)
    # without modifying KiboAgent interface or packing it in input.

    # For now, let's just verify compiling succeeded with extensions.
    print("Workflow compiled successfully with native MemorySaver!")

    kibo_agent = KiboAgent(
        config=AgentConfig(
            name="Runner",
            description="",
            instructions="",
            agent="langgraph",
            model="gpt-4",
        ),
        adapter=adapter,
    )

    try:
        # Simple run with Checkpointer config passed as params
        # Kibo now supports passing execution params which are forwarded as config to LangGraph
        result = kibo_agent.run(
            {"messages": [HumanMessage(content="Persistence test")]},
            params={"configurable": {"thread_id": "1"}},
        )
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
