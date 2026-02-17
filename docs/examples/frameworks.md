# Framework Integration Examples

Kibo unifies multiple AI frameworks under a single API. Here are examples of using Kibo with various underlying engines.

## Agno (formerly PhiData)
Location: `examples/frameworks/agno/`

*   **Gemini Integration**: `agno_native_gemini_example.py` - Using Google Gemini models.
*   **OpenAI Integration**: `agno_openai_example.py` - Using OpenAI models.
*   **Tool Usage**: `agno_tool_example.py` - Demonstrating native tool integration (e.g., YFinance).

```python
import os
from kibo_core import AgentConfig, create_agent


def main():
    print("--- Agno (PhiData) + OpenAI + Kibo Blueprint Example ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        return

    agent_def = AgentConfig(
        name="ScienceBot",
        description="You are a helpful science assistant.",
        instructions="Explain complex topics simply.",
        agent="agno",
        model="gpt-4o-mini",
        config={"markdown": True},
    )

    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching task...")
    try:
        result = agent.run("Explain Quantum Computing in 1 sentence.")

        print("\nResult:")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
```

```bash
uv run examples/frameworks/agno/agno_native_gemini_example.py
```

## CrewAI
Location: `examples/frameworks/crewai/`

*   **Basic Agent**: `crewai_example.py`
*   **Gemini/OpenAI**: Specific vendor implementations.
*   **Tool Usage**: `crewai_tool_example.py` - Using tools within a Kibo-wrapped CrewAI agent.

```python
import sys
import os
from kibo_core import AgentConfig, create_agent


def main():
    print("--- CrewAI + OpenAI + Kibo Blueprint Example ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    agent_def = AgentConfig(
        name="Economist",
        description="You are an expert in budget optimization.",
        instructions="Analyze cost-effective AI strategies.",
        agent="crewai",
        model="gpt-4o-mini",
        config={"verbose": True, "allow_delegation": False},
    )

    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching Crew to Kibo Cluster...")
    try:
        input_data = "saving money on LLM API usage"

        task = agent.run_async(input_data)
        result = task.result()

        print("\n--- Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
```


## LangChain
Location: `examples/frameworks/langchain/`

*   **Basic Agent**: `langchain_example.py`
*   **Tool Usage**: `langchain_tool_example.py`
*   **Vendor Integrations**: OpenAI and Gemini examples.

```python
import sys
import os
from kibo_core import AgentConfig, create_agent


def main():
    print("--- LangChain + OpenAI + Kibo Blueprint Example ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    agent_def = AgentConfig(
        name="JesterAI",
        description="A funny bot backed by OpenAI",
        instructions="Tell me a short joke about the topic provided by the user.",
        agent="langchain",
        model="gpt-4o-mini",
    )

    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching job to Kibo Cluster...")
    try:
        result = agent.run("saving money")

        print("\n--- Result ---")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
```


## LangGraph
Location: `examples/frameworks/langgraph/`

Examples showing how Kibo can orchestrate LangGraph-based flows.

```python
import os
import operator
from dotenv import load_dotenv
from typing import Annotated, TypedDict, List
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from kibo_core import AgentConfig, create_agent
from kibo_core.infrastructure.adapters.langgraph_adapter import LangGraphAdapter


class AgentState(TypedDict):
    """
    State definition for the multi-step graph.
    """

    messages: Annotated[List[BaseMessage], operator.add]
    topic: str
    draft: str
    critique: str


def writer_node(state: AgentState):
    """Generates a draft using a creative model (e.g. gpt-4o-mini)."""
    print("--- Step 1: Writer Node ---")
    topic = state.get("topic", "Technology")

    # Simulate using a specific model configuration
    # Note: Kibo's api_key can be passed down, but for raw LangGraph usage,
    # we assume environment variable or explicit passing.
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    response = llm.invoke(
        [
            SystemMessage(
                content="You are a technical writer. Write a short explanation about the topic."
            ),
            HumanMessage(content=f"Write about: {topic}"),
        ]
    )

    return {"draft": response.content, "messages": [response]}


def reviewer_node(state: AgentState):
    """Reviews the draft using a more critical model."""
    print("--- Step 2: Reviewer Node ---")
    draft = state.get("draft", "")

    # Simulate using a different model configuration
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

    response = llm.invoke(
        [
            SystemMessage(
                content="You are an editor. Review the draft criticaly in 1 sentence."
            ),
            HumanMessage(content=f"Review this draft: {draft}"),
        ]
    )

    return {"critique": response.content, "messages": [response]}


def finalizer_node(state: AgentState):
    """Finalizes the content based on critique."""
    print("--- Step 3: Finalizer Node ---")
    draft = state.get("draft")
    critique = state.get("critique")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

    response = llm.invoke(
        [
            SystemMessage(content="Improve the draft based on the critique."),
            HumanMessage(content=f"Draft: {draft}\nCritique: {critique}"),
        ]
    )

    # Return the final message content as the last message for the adapter to pick up
    return {"messages": [response]}


def main():
    print("--- Complex LangGraph + Kibo Example ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set.")
        # return # Allow to crash if user wants to see import success

    # --- 1. Define the Custom Graph ---
    workflow = StateGraph(AgentState)

    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("finalizer", finalizer_node)

    # Define edges
    workflow.add_edge(START, "writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_edge("reviewer", "finalizer")
    workflow.add_edge("finalizer", END)

    app = workflow.compile()

    # --- 2. Create Adapter ---
    # We manually wrap the compiled graph
    custom_adapter = LangGraphAdapter(app)

    # --- 3. Use Kibo to Execute ---
    # We define a dummy config because we supply our own adapter
    agent_def = AgentConfig(
        name="ContentTeam",
        description="Multi-model writing team",
        instructions="N/A",
        agent="langgraph",
        model="mixed",
    )

    # Pass the adapter to run it via Kibo infrastructure (local or distributed)
    kibo_agent = create_agent(agent_def, api_key=api_key, adapter=custom_adapter)

    print("Dispatching task via Kibo Agent...")
    try:
        # Input matching our State definition
        input_data = {"topic": "Event Driven Architecture"}

        result = kibo_agent.run(input_data)

        print("\n--- Final Kibo Result ---")
        print(f"Output: {result.output_data}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
```


## PydanticAI
Location: `examples/frameworks/pydantic_ai/`

Demonstrating the integration with PydanticAI for type-safe agent interactions.

```python
import os
from kibo_core import AgentConfig, create_agent


def main():
    print("--- PydanticAI + OpenAI + Kibo Blueprint Example ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        return

    agent_def = AgentConfig(
        name="GeneralBot",
        description="A general purpose assistant",
        instructions="You are a helpful assistant.",
        agent="pydantic-ai",
        model="gpt-4o-mini",
    )

    agent = create_agent(agent_def, api_key=api_key)

    print("Dispatching task...")
    try:
        result = agent.run("What is the capital of France?")

        print("\nResult:")
        print(result.output_data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
```

