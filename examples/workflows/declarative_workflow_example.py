import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from kibo_core.domain.blueprint import AgentConfig
from kibo_core.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kibo_core import create_workflow, KiboAgent
from langchain_core.messages import HumanMessage


def main():
    print("--- Declarative Workflow Example (Engine Agnostic) ---")

    api_key = os.getenv("OPENAI_API_KEY")

    # 1. Define Atomic Agents (Reused across workflows)
    writer_agent = AgentConfig(
        name="TechWriter",
        description="Technical writer",
        instructions="Complete the writing task based on input.",
        model="gpt-4o-mini",
    )

    editor_agent = AgentConfig(
        name="EditorBot",
        description="Senior Editor",
        instructions="Review and critique the provided draft.",
        model="gpt-4o-mini",
    )

    # 2. Define the Workflow Abstractly
    # This structure can run on ANY engine (LangGraph, CrewAI, etc)
    workflow_def = WorkflowConfig(
        name="BlogPipeline",
        description="Write and review a blog post.",
        engine="langgraph",  # Change to "crewai" to switch runtime!
        start_step="draft_step",
        steps=[
            WorkflowStep(
                id="draft_step",
                agent=writer_agent,
                instruction="Write a draft about: {input}",
                next="review_step",
            ),
            WorkflowStep(
                id="review_step",
                agent=editor_agent,
                instruction="Review the draft above for clarity.",
                next=None,  # End
            ),
        ],
    )

    print(f"Compiling workflow to engine: {workflow_def.engine}")

    # 3. Create the Executable (Adapter)
    adapter = create_workflow(workflow_def, api_key=api_key)

    # 4. Use standard Kibo Execution
    # We create a dummy agent wrapper just to access .run() features like distributed mode
    # In a real app, create_workflow might return a KiboAgent directly.
    kibo_agent = KiboAgent(
        config=AgentConfig(
            name="WorkflowRunner",
            description="Runner",
            instructions="",
            agent="langgraph",  # Placeholder
            model="gpt-4",
        ),
        adapter=adapter,
    )

    print("Running Workflow...")
    try:
        input_data = {"messages": [HumanMessage(content="The future of AI Agents")]}

        result = kibo_agent.run(input_data)

        print("\n--- Workflow Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
