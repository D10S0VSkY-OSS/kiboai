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

Kibo provides a **Declarative Graph API** (`KiboGraph`) that abstracts the complexity of building LangGraph workflows. Instead of manually defining state classes and graph compilers, you can define your agents and flows declaratively.

### Core Components

*   **`KiboGraph`**: The abstract definition of your workflow. It holds the `StateSchema`, the list of `Nodes` (Agents), and the `Edges` (Connections) between them.
*   **`AgentConfig`**: Defines each node in the graph. You can specify the model, instructions, and tools for each step independently.
*   **`compile_graph`**: A utility that transforms your static `KiboGraph` definition into a runnable LangGraph `StateGraph` adapter.
*   **`KiboAgent`**: The universal execution runtime. It wraps the compiled graph and exposes a consistent `.run()` method, handling both local execution and distributed deployment on Ray.

### Use Cases

1.  **Sequential Pipelines**: Linear workflows like `Research -> Draft -> Edit -> Publish`.
2.  **Multi-Model Workflows**: Assigning specific models to specific steps (e.g., Gemini for creative writing, OpenAI for strict logical review).
3.  **Stateful Orchestration**: Managing complex context where multiple agents contribute to a shared state object.

### Example 1: OpenAI Sequential Workflow
This example demonstrates a 3-step content pipeline (Writer -> Editor -> Publisher) using OpenAI models.

File: `examples/frameworks/langgraph/langgraph_openai_example.py`

```python
import os
from typing import Annotated, Dict, List, TypedDict, Union
import operator
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage

from kibo_core import AgentConfig, KiboAgent
from kibo_core.domain.graph import KiboGraph, START, END
from kibo_core.infrastructure.graph_compiler import compile_graph

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
        config={"temperature": 0.7}
    )

    reviewer = AgentConfig(
        name="Editor",
        description="Critique the draft.",
        instructions="You are an editor. Review the previous text critically in 1 sentence.",
        model="gpt-4o-mini",
        config={"temperature": 0.0}
    )

    finalizer = AgentConfig(
        name="Publisher",
        description="Finalize the text.",
        instructions="Improve the draft based on the critique provided in the conversation history.",
        model="gpt-4o-mini",
        config={"temperature": 0.5}
    )

    # 2. Define the Graph Structure Declaratively
    # 'KiboGraph' abstracts away the underlying StateGraph
    graph = KiboGraph(
        name="ContentPipeline",
        state_schema=AgentState,
        entry_point="writer"
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
            model="mixed"
        ),
        adapter=adapter
    )

    print("Dispatching task via Kibo Graph...")
    try:
        # Input matching our State definition
        # Kibo's compiler wrapper automatically handles passing this inputs to the first agent
        # Input can be a string (topic) or a dict matching the state
        input_data = {"topic": "Event Driven Architecture"}
        
        # When using LangGraph adapter with simpler inputs, we might need to conform to state schema
        # The wrapper aims to be flexible.
        
        result = kibo_agent.run(input_data)
        
        print("\n--- Result ---")
        # For LangGraph, output_data is usually the final state dict
        print(result.output_data)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

### Example 2: Gemini Native Integration
This example shows how to use native objects (like `ChatGoogleGenerativeAI`) directly within Kibo's graph definition. This is useful when you need specific provider features not covered by generic string identifiers.

File: `examples/frameworks/langgraph/langgraph_native_gemini_example.py`

```python
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

from kibo_core import AgentConfig, KiboAgent
from kibo_core.domain.graph import KiboGraph, START, END
from kibo_core.infrastructure.graph_compiler import compile_graph


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
        model=native_model, # Pass the object directly
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
        name="GeminiContentPipeline",
        state_schema=AgentState,
        entry_point="writer"
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
            model="mixed" # Placeholder
        ),
        adapter=adapter
    )

    print("Dispatching task via Kibo Graph (Gemini)...")
    try:
        # Input matching our State definition
        # Manually constructing the initial state
        initial_message = HumanMessage(content="Explain Quantum Computing")
        input_data = {
            "messages": [initial_message],
            "topic": "Quantum Computing"
        }
        
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
                print(f"{prefix}: {content[:100]}..." if len(content) > 100 else f"{prefix}: {content}")
        else:
            print(result.output_data)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

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

