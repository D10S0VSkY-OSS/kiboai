import os
import sys

# Add src to path just in case
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from dotenv import load_dotenv
from typing import Dict, Any

from kiboai.domain.blueprint import AgentConfig
from kiboai.domain.workflow_definitions import WorkflowConfig, WorkflowStep
from kiboai import create_workflow, KiboAgent

# Import Native Agno Class
try:
    from agno.models.google import Gemini
except ImportError:
    print("Please install google-generativeai: pip install google-generativeai")
    exit(1)

load_dotenv()


def main():
    print("--- Native Gemini Workflow Example (Agno Engine) ---")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY is not set.")
        return

    # 1. Define Native Model for Steps
    native_gemini_model = Gemini(id="gemini-2.0-flash", api_key=api_key)

    # 2. Define Workflow Steps with Native Model
    step_agent = AgentConfig(
        name="GeminiResearcher",
        description="A researcher powered directly by Google Gemini.",
        instructions="Provide detailed research.",
        model=native_gemini_model,  # <--- Native Model Object
        agent="agno",  # Using Agno framework for the step agent
    )

    workflow_def = WorkflowConfig(
        name="GeminiResearchFlow",
        description="Simple research flow using native Gemini models.",
        engine="agno",
        start_step="research",
        steps=[
            WorkflowStep(
                id="research",
                agent=step_agent,
                instruction="Explain the concept of 'Quantum Entanglement' simply.",
                next=None,
            ),
        ],
        # Optional: Configure the Manager/Team Leader to also use Gemini via LiteLLM string mode
        # or just let it default to LiteLLM(gpt-4o) if available, but let's try to force Gemini for consistency
        # Kibo workflow factory for Agno uses 'model' in native_extensions for the manager.
        native_extensions={
            "model": "gemini/gemini-2.0-flash",  # String mode (Universal LiteLLM) for manager
            # We could also pass an object here if we modify workflow_factory_agno further to support it!
            # But currently my fix only supported LiteLLM fallback for strings.
            # Let's stick to string for manager to test the new fallback logic.
        },
    )

    # 3. Compile & Run
    print("Compiling workflow...")
    # API Key is passed for the manager if it needs it (LiteLLM uses env vars usually)
    # We pass the Google API Key explicitly so the Manager (Team Leader) can use it via LiteLLM
    adapter = create_workflow(workflow_def, api_key=api_key)

    # Wrap in KiboAgent to execute
    kibo_agent = KiboAgent(
        config=AgentConfig(
            name="WorkflowRunner",
            description="Runner",
            instructions="",
            agent="agno",
            model="gpt-4o",  # Dummy, not used by adapter execution
        ),
        adapter=adapter,
    )

    print("Running Workflow...")
    try:
        # Agno workflows (Teams) take a string prompt usually
        result = kibo_agent.run("Start research.")
        print("\n--- Workflow Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error executing workflow: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
