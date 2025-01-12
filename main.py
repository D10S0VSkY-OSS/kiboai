from kibo_core.infrastructure.adapters.base import MockEchoAgentAdapter
from kibo_core.application.workflow import DistributedWorkflowService
import sys

def main():
    print("Initializing Distributed Kibo Framework...")
    
    service = DistributedWorkflowService()
    
    agent = MockEchoAgentAdapter()
    
    custom_params = {
        "echo_prefix": "Ray says: "
    }
    
    print("Dispatching task to Ray cluster...")
    try:
        result = service.run_agent_task(
            agent=agent, 
            input_data="Hello World from Distributed Python!", 
            params=custom_params
        )
        
        print("\n--- Result Received ---")
        print(f"Output: {result.output_data}")
        print(f"Metadata: {result.metadata}")
        
    except Exception as e:
        print(f"Error executing task: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
