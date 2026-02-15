import os
from dotenv import load_dotenv

from kibo_core.domain.blueprint import AgentConfig
from kibo_core.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kibo_core import create_workflow, KiboAgent

# Load environment variables
load_dotenv()


def main():
    print("--- Declarative Team Example (Engine: Agno) ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        return

    # 1. Define Team Members
    researcher = AgentConfig(
        name="Researcher",
        description="Web Researcher",
        instructions="Search for information about the user's query.",
        model="gpt-4o-mini",
        # Kibo tools are automatically converted to Agno tools by the factory!
        config={"tools": ["duckduckgo"]},
    )

    summarizer = AgentConfig(
        name="Summarizer",
        description="Content Summarizer",
        instructions="Summarize the information found by the researcher concisely.",
        model="gpt-4o-mini",
    )

    # 2. Define Workflow as a Team
    # In Agno, this compiles to a 'Leader' agent that has 'Researcher' and 'Summarizer' in its team.
    # The 'steps' logic in Agno is handled by the Leader's LLM planning,
    # unlike the explicit steps in LangGraph. But Kibo maps it nicely.
    workflow_def = WorkflowConfig(
        name="ResearchTeam",
        description="A team that researches and summarizes topics.",
        engine="agno",
        start_step="research",  # Logic is less strict in Agno, but we keep structure
        steps=[
            WorkflowStep(
                id="research",
                agent=researcher,
                instruction="Find latest news about {input}",
                next="summarize",
            ),
            WorkflowStep(
                id="summarize",
                agent=summarizer,
                instruction="Summarize the findings.",
                next=None,
            ),
        ],
        # Example of Native Extension: Passing instructions to the Team Leader
        native_extensions={
            "instructions": "First ask the Researcher to find info, then ask Summarizer to condense it."
        },
    )

    print(f"Compiling workflow to engine: {workflow_def.engine}")

    # 3. Create & Execute
    adapter = create_workflow(workflow_def, api_key=api_key)

    kibo_agent = KiboAgent(
        config=AgentConfig(
            name="AgnoRunner",
            description="",
            instructions="",
            agent="agno",
            model="gpt-4o",
        ),
        adapter=adapter,
    )

    print("Running Agno Workflow...")
    try:
        # Agno usually takes a string prompt
        input_data = "What is 2+2?"

        result = kibo_agent.run(input_data)

        print("\n--- Team Result ---")
        print(result.output_data)

        print("\n--- Metadata Analysis ---")
        meta = result.metadata
        print(f"1. Adapter Source: {meta.get('adapter')} (Kibo Wrapper)")

        usage = meta.get("usage")
        print(f"2. Framework Object (Agno): {type(usage).__name__}")
        print(f"   {usage}")

        # Try to show raw-like values usually returned by LiteLLM/OpenAI
        print("3. Underlying Data (Simulating LiteLLM Response):")
        if usage:
            # Agno Metrics object attributes
            input_tok = getattr(usage, "input_tokens", 0)
            output_tok = getattr(usage, "output_tokens", 0)
            total_tok = getattr(usage, "total_tokens", 0)
            print(
                f"   {{'prompt_tokens': {input_tok}, 'completion_tokens': {output_tok}, 'total_tokens': {total_tok}}}"
            )

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
