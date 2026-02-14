# Parallel Execution

This example demonstrates running multiple agents concurrently using Kibo's distributed mode.

## Source Code
`examples/parallel_execution_example.py`

```python
--8<-- "examples/parallel_execution_example.py"
```

## How it works

1.  **Configuration**: We define agents with `distributed=True` in their `AgentConfig`. This signals Kibo to spawn them as generic worker actors in the Ray cluster.
2.  **Creation**: We loop through a list of tasks, creating a new "Mock" agent for each one to simulate workload.
3.  **Dispatch**: We call `run_async()`, which immediately returns a `KiboFuture` while the task runs in the background.
4.  **Collection**: We use `future.result()` to retrieve the output once processing is complete.

## Performance
By running these tasks in parallel, the total execution time is roughly equal to the longest single task, rather than the sum of all tasks (sequential).
