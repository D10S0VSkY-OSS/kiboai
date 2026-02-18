import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kiboai import AgentConfig, create_agent


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
