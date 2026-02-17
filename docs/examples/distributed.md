# Distributed & Parallel Execution

One of Kibo's core strengths is its ability to scale agent execution using Ray.

## Parallel Execution
Location: `examples/distributed/parallel_execution_example.py`

Demonstrates running multiple agents concurrently. This example dispatches multiple tasks and waits for them to complete in parallel, utilizing the Ray backend.

```python
import sys
import os
import time
from kibo_core import AgentConfig, create_agent


def main():
    print("--- Kibo Parallel Execution Example (Blueprint) ---")

    tasks = [
        ("Task A", 2),
        ("Task B", 2),
        ("Task C", 2),
        ("Task D", 2),
        ("Task E", 2),
    ]

    print(f"\nSubmitting {len(tasks)} tasks to Kibo...")
    start_time = time.time()

    futures = []

    for name, duration in tasks:
        agent_def = AgentConfig(
            name=f"Worker-{name}",
            description="Simulates work.",
            instructions="Sleep for a bit.",
            agent="mock",
            model="none",
            distributed=True,
            config={"duration": duration},
        )

        agent = create_agent(agent_def)
        future = agent.run_async(name)

        futures.append(future)
        print(f"Submitted {name}")

    print("\nAll tasks submitted. Waiting for results...")

    results = [f.result() for f in futures]

    end_time = time.time()
    total_time = end_time - start_time

    print("\n--- Results ---")
    for res in results:
        node = res.metadata.get("node", "unknown")
        pid = res.metadata.get("pid", "unknown")
        print(f" - {res.output_data} | Executed on: {node} (PID: {pid})")

    print(f"\nTotal execution time: {total_time:.2f} seconds")

    seq_time = sum(t[1] for t in tasks)
    print(f"Theoretical sequential time: {seq_time:.2f} seconds")
    print(f"Speedup: {seq_time / total_time:.2f}x")


if __name__ == "__main__":
    main()
```

```bash
uv run examples/distributed/parallel_execution_example.py
```

## Distributed Patterns

### Declarative Distributed
Location: `examples/distributed/distributed_declarative_example.py`

Configuring distributed execution via the `AgentConfig`.

```python
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kibo_core import AgentConfig, create_agent


def main():
    print("Example 1: Distributed Execution via Configuration (Declarative)")

    # Define Agent Config with distributed=True
    config = AgentConfig(
        name="ClusterAgent",
        description="An agent configured to always run on the cluster.",
        instructions="Return a greeting identifying your execution environment.",
        agent="mock",  # Use Mock agent for simplicity
        distributed=True,  # <--- KEY CONFIGURATION
        config={"echo_prefix": "Cluster Config Says: "},
    )

    # Create Agent (will connect to Ray automatically)
    agent = create_agent(config, api_key="sk-dummy")

    print("Dispatching task...")
    try:
        result = agent.run("Hello Kibo!")
        print(f"Result: {result.output_data}")
        print(f"Metadata: {result.metadata}")
    except Exception as e:
        print(f"Execution failed: {e}")


if __name__ == "__main__":
    main()
```

### Imperative Distributed
Location: `examples/distributed/distributed_imperative_example.py`

Manually managing distributed primitives.

```python
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kibo_core import AgentConfig, create_agent


def main():
    print("Example 2: Distributed Execution via Runtime Override (Imperative)")

    # Define Agent Config as LOCAL by default (distributed=False default)
    config = AgentConfig(
        name="HybridAgent",
        description="An agent capable of running anywhere.",
        instructions="Return a greeting identifying your execution environment.",
        agent="mock",
        config={"echo_prefix": ""},
    )

    # Create Agent (initialized locally by default)
    agent = create_agent(config, api_key="sk-dummy")

    print("\n--- Phase 1: Running Locally ---")
    res_local = agent.run("Hello Local World!", distributed=False)
    print(f"Local Result: {res_local.output_data}")
    print(
        f"Local Metadata: {res_local.metadata}"
    )  # Should say 'node': 'local' or verify executor

    print("\n--- Phase 2: Running Distributed ---")
    try:
        # Override execution mode at runtime
        res_dist = agent.run("Hello Distributed World!", distributed=True)
        print(f"Distributed Result: {res_dist.output_data}")
        print(f"Distributed Metadata: {res_dist.metadata}")
    except Exception as e:
        print(f"Distributed execution failed (Ensure 'kibo start-all' is running): {e}")


if __name__ == "__main__":
    main()
```
