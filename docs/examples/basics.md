# Basic Examples

This section introduces the fundamental concepts of Kibo AI through simple examples.

## Blueprint Example
Location: `examples/basics/blueprint_example.py`

This example demonstrates how to define an agent using the `AgentConfig` blueprint. It shows the core "Zero-Dependency" philosophy where agent behavior is defined in pure Python data structures.

```python
import os
from kibo_core import AgentConfig, create_agent


def main():
    print("--- Kibo Blueprint Example (Zero-Dependency Definition) ---")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set.")
        return

    my_agent_def = AgentConfig(
        name="AnalystBot",
        description="You are a senior data analyst with a sarcastic personality.",
        instructions="Analyze the user input and provide a summary with 3 bullet points.",
        agent="agno",
        model="gpt-4o-mini",
        distributed=True,
        config={"markdown": True},
    )

    agent = create_agent(my_agent_def, api_key=api_key)

    print(f"Dispatching task to {my_agent_def.agent} engine...")
    try:
        result = agent.run("Comparison between Rust and Python performance.")

        print("\n--- Result ---")
        print(result.output_data)
        print(f"\nMetadata: {result.metadata}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
```

```bash
uv run examples/basics/blueprint_example.py
```
