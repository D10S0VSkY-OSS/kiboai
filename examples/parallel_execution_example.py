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
            config={"duration": duration}
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
