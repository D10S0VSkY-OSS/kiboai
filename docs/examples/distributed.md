# Distributed & Parallel Execution

One of Kibo's core strengths is its ability to scale agent execution using Ray.

## Parallel Execution
Location: `examples/distributed/parallel_execution_example.py`

Demonstrates running multiple agents concurrently. This example dispatches multiple tasks and waits for them to complete in parallel, utilizing the Ray backend.

## Distributed Patterns

*   **Declarative Distributed**: `examples/distributed/distributed_declarative_example.py` - Configuring distributed execution via the AgentConfig.
*   **Imperative Distributed**: `examples/distributed/distributed_imperative_example.py` - Manually managing distributed primitives.

```bash
uv run examples/distributed/parallel_execution_example.py
```
