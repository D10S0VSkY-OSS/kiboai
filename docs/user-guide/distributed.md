# Distributed & Parallel Execution

Kibo leverages **Ray** to enable true distributed execution of AI agents. This allows you to scale from running multiple agents in parallel on a single machine to running them across a cluster of servers.

## Local vs. Distributed Mode

### Local Mode (Default)
By default (`distributed=False`), Kibo runs agents in the same process or using standard thread pools. This is ideal for:
- Development and debugging.
- Simple, low-latency tasks.
- Environments where installing Ray is not possible.

### Distributed Mode
When `distributed=True` is set, Kibo spins up a Ray cluster (if one isn't already running) and deploys each agent as a separate **Ray Actor**. This is ideal for:
- Heavy computational tasks.
- Running massive numbers of agents in parallel.
- Workflows that need to survive a single process crash.

## Enabling Distributed Execution

You can enable distributed execution in two ways:

1.  **Via Agent Config:**
    ```python
    config = AgentConfig(
        name="Worker", 
        agent="crewai", 
        distributed=True,  # <--- Here
        ...
    )
    ```

2.  **Via Factory:**
    ```python
    agent = create_agent(config, enable_distributed_execution=True)
    ```

## Example: Parallel Execution

See `examples/parallel_execution_example.py` for a complete runnable script.

```python
import time
from kibo_core import AgentConfig, create_agent

tasks = ["Task A", "Task B", "Task C"]
futures = []

print("Submitting tasks...")
for name in tasks:
    # 1. Configure agent to run distributed
    config = AgentConfig(
        name=name,
        instructions="Work hard",
        agent="mock",
        distributed=True
    )
    
    # 2. Create agent
    agent = create_agent(config)
    
    # 3. Submit async task
    # This returns immediately while the agent runs on a Ray worker
    future = agent.run_async("Start")
    futures.append(future)

# 4. Gather results
print("Waiting for results...")
results = [f.result() for f in futures]
```

## Managing the Cluster

You can manage the Kibo runtime using the CLI:

```bash
# Start a head node (on your main machine)
uv run kibo start --head

# Stop the cluster
uv run kibo stop
```
