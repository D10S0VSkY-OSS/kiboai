from kibo_core.infrastructure.adapters.base import MockEchoAgentAdapter
from kibo_core.application.workflow import DistributedWorkflowService
import sys

def main():
    print("Initializing Distributed Kibo Framework...")
    
    # 1. Setup Service
    service = DistributedWorkflowService()
    
    # 2. Setup Agent (In real life, this is LangGraph/CrewAI adapter)
    agent = MockEchoAgentAdapter()
    
    # 3. Define specific params (The "Pass-Through" feature)
    # These params are invisible to the core framework but visible to the agent
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
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
