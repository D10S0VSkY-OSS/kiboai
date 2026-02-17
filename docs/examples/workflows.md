# Workflow Examples

Kibo supports orchestrating complex sequences of tasks, allowing you to chain agents together.

## Declarative Workflows (YAML-style)
Location: `examples/workflows/declarative_workflow_example.py`

Define your entire multi-step process in a simple configuration object (or YAML file). This example shows how to chain a research agent into a writer agent.

```python
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
```

```bash
uv run examples/workflows/declarative_workflow_example.py
```

## Native Tool Integration
Location: `examples/workflows/workflow_native_gemini_example.py`

Execute workflows using Gemini models with native function calling capabilities.

```bash
uv run examples/workflows/workflow_native_gemini_example.py
```

## Framework-Specific Workflows

### Agno (PhiData)
Location: `examples/workflows/agno_workflow_example.py`

Basic chaining of Agno agents.

```python
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

        # ... (metadata analysis omitted for brevity) ...

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
```

*   **Translation Workflow**: `examples/workflows/agno_workflow_translation.py` - A pipeline for translating content.

### CrewAI
*   **Declarative Config**: `examples/workflows/crewai_declarative_example.py` - Configuring a CrewAI process using Kibo's declarative syntax.

## Native Extensions
Location: `examples/workflows/native_extensions_example.py`

Demonstrates how to pass low-level configuration options (like specific graph state definitions or CrewAI process overrides) to the underlying engine while still using Kibo's high-level API.

```bash
uv run examples/workflows/native_extensions_example.py
```
