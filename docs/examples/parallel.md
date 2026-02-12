# Parallel Execution

This example demonstrates running multiple agents concurrently.

`examples/parallel_execution_example.py`

```python
--8<-- "examples/parallel_execution_example.py"
```

## How it works

1.  **Creation**: We create a list of agents (Poet, Joker, Historian).
2.  **Dispatch**: We loop through them calling `run_async()`, collecting the futures.
3.  **Collection**: We verify the results.
