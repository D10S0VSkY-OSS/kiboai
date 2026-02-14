import os
from dotenv import load_dotenv
from kibo_core.domain.blueprint import AgentConfig
from kibo_core.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kibo_core import create_workflow, KiboAgent
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()


def main():
    print("--- Declarative Workflow Example (Engine: CrewAI) ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set in .env file.")
        return

    # 1. Define Atomic Agents
    analyst_agent = AgentConfig(
        name="MarketAnalyst",
        description="Senior Market Analyst",
        instructions="Analyze the given market topic and provide top 3 trends.",
        model="gpt-4o-mini",
    )

    writer_agent = AgentConfig(
        name="ContentWriter",
        description="Tech Blogger",
        instructions="Write an engaging blog post based on the trends provided.",
        model="gpt-4o-mini",
    )

    # 2. Define the Workflow Abstractly
    # This same structure is compiled to CrewAI Agents and Tasks
    workflow_def = WorkflowConfig(
        name="MarketTrendsBlog",
        description="Analyze market and write blog",
        engine="crewai",  # Selecting CrewAI engine
        start_step="analyze_step",
        steps=[
            WorkflowStep(
                id="analyze_step",
                agent=analyst_agent,
                instruction="Analyze trends for: {input}",
                next="write_step",
            ),
            WorkflowStep(
                id="write_step",
                agent=writer_agent,
                instruction="Write blog post using these trends.",
                next=None,  # End
            ),
        ],
    )

    print(f"Compiling workflow to engine: {workflow_def.engine}")

    # 3. Create the Executable (Adapter)
    adapter = create_workflow(workflow_def, api_key=api_key)

    # 4. Execute
    kibo_agent = KiboAgent(
        config=AgentConfig(
            name="CrewRunner",
            description="Runner",
            instructions="",
            agent="crewai",
            model="gpt-4",
        ),
        adapter=adapter,
    )

    print("Running CrewAI Workflow...")
    try:
        # CrewAI typically takes a string topic or a dict
        input_data = "AI Agents in 2026"

        result = kibo_agent.run(input_data)

        print("\n--- Workflow Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
