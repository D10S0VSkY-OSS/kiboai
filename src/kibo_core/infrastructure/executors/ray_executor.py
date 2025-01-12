import ray
from typing import Any, Type
from kibo_core.domain.ports import IAgentNode
from kibo_core.domain.entities import AgentRequest, AgentResult
from kibo_core.infrastructure.runtime import kibo_init

class RayDistributedExecutor:
    """
    Infrastructure service that executes agents on a Ray cluster.
    """
    def __init__(self, address: str = None):
        """
        Initialize Ray.
        If address is provided, connects to that cluster.
        If address is None or 'auto', tries to connect to existing cluster, 
        falls back to starting a local instance.
        """
        kibo_init(address=address)

    def execute_remote(self, agent_adapter: IAgentNode, request: AgentRequest) -> Any:
        # Note: Passing the actual instance might be tricky if it's not picklable.
        # Ideally, we pass the class and config to instantiate it remotely.
        # For this PoC, we assume the adapter is an Actor or we wrap it in a Task.
        
        # Strategy: Use a Generic Ray Runner Actor
        # This creates a Ray Actor that wraps our Domain Agent
        runner = RemoteAgentRunner.remote(agent_adapter)
        return runner.run.remote(request)

@ray.remote
class RemoteAgentRunner:
    def __init__(self, agent_adapter: IAgentNode):
        self.agent = agent_adapter

    def run(self, request: AgentRequest) -> AgentResult:
        return self.agent.execute(request)
