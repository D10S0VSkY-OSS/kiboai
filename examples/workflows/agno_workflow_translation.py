import os
import sys

# Add src to path just in case
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from dotenv import load_dotenv

from kiboai.domain.blueprint import AgentConfig
from kiboai.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kiboai import create_workflow, KiboAgent

load_dotenv()

# Native Agno Tool Import
try:
    from agno.tools.hackernews import HackerNewsTools
except ImportError:
    print("Warning: agno tools not found, using mock.")

    class HackerNewsTools:
        pass


def main():
    print("--- Translating Agno Workflow to Kibo ---")

    api_key = os.getenv("OPENAI_API_KEY")
    # If using other providers, ensure their keys are set

    # 1. Translate 'Researcher' Agent
    print("Defining Researcher Agent...")
    # Original:
    # researcher = Agent(
    #     name="Researcher",
    #     instructions="Find relevant information about the topic",
    #     tools=[HackerNewsTools()]
    # )

    # Kibo Translation:
    researcher = AgentConfig(
        name="Researcher",
        description="Researcher",  # Description is mandatory in Kibo
        instructions="Find relevant information about the topic",
        model="gpt-4o-mini",
        # Pass native tool directly. Kibo passes it through to Agno.
        config={"tools": [HackerNewsTools()]},
    )

    # 2. Translate 'Writer' Agent
    print("Defining Writer Agent...")
    # Original:
    # writer = Agent(
    #     name="Writer",
    #     instructions="Write a clear, engaging article based on the research"
    # )

    # Kibo Translation:
    writer = AgentConfig(
        name="Writer",
        description="Writer",
        instructions="Write a clear, engaging article based on the research",
        model="gpt-4o-mini",
    )

    # 3. Translate Workflow
    print("Defining Workflow Structure...")
    # Original step sequential logic is mapped to Kibo Steps
    # content_workflow = Workflow(
    #     name="Content Creation",
    #     steps=[researcher, writer]
    # )

    # Kibo Translation:
    workflow_def = WorkflowConfig(
        name="Content Creation",
        description="A workflow that researches a topic and writes an article about it.",
        engine="agno",
        start_step="research",
        steps=[
            WorkflowStep(
                id="research",
                agent=researcher,
                # The prompt/instruction explicitly tells the Manager what this step does
                instruction="Research about: {input}",
                next="write",
            ),
            WorkflowStep(
                id="write",
                agent=writer,
                instruction="Write article based on the research findings.",
                next=None,
            ),
        ],
    )

    print("Compiling Kibo Workflow (Agno Backend)...")
    adapter = create_workflow(workflow_def, api_key=api_key)

    # 4. Execution wrapper
    kibo_agent = KiboAgent(
        config=AgentConfig(
            name="Runner",
            description="Runner",
            instructions="",
            agent="agno",
            model="gpt-4o",
        ),
        adapter=adapter,
    )

    print("\nRunning Workflow: 'Write an article about AI trends'")
    # content_workflow.print_response("Write an article about AI trends", stream=True)

    try:
        # Kibo runs synchronously and returns full result for now
        result = kibo_agent.run("Write an article about AI trends")

        print("\n--- Final Kibo Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error executing workflow: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
