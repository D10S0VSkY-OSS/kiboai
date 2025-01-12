# Distributed Execution

Kibo runs on **Ray**, allowing easy parallelization.

## The Async Pattern

When you use `run_async`, Kibo submits the task to the Ray cluster (or local Ray instance). It returns a `KiboFuture`.

Because `KiboFuture.result()` internally calls `ray.get()`, it is a blocking operation. To check results asynchronously in an `asyncio` loop, wrap it:

```python
import asyncio
from kibo_core import create_agent, AgentConfig

async def gather_results(agents, inputs):
    # 1. Dispatch all tasks (Non-blocking submit)
    futures = [agent.run_async(inp) for agent, inp in zip(agents, inputs)]
    
    # 2. Wait for them concurrently
    # We use to_thread because .result() blocks the CPU
    results = await asyncio.gather(
        *[asyncio.to_thread(f.result) for f in futures]
    )
    return results
```

## Running the Cluster

For true distributed execution across nodes:

1.  Start the **Head Node**:
    ```bash
    uv run kibo start --head --port=6379
    ```
2.  Start **Worker Nodes** (on other machines):
    ```bash
    uv run kibo start --address='<HEAD_IP>:6379'
    ```

Kibo will automatically schedule tasks across the available resources.
