from typing import Any, Optional
import kibo_core
from kibo_core.domain.blueprint import AgentConfig
from kibo_core.application.workflow import DistributedWorkflowService
from kibo_core.application.factory import create_distributed_agent
from kibo_core.domain.entities import AgentResult

class KiboFuture:
    def __init__(self, future):
        self._future = future

    def result(self) -> AgentResult:
        """
        Blocking wait for the result.
        Returns the AgentResult object (containing output_data and metadata).
        """
        return kibo_core.get(self._future)

class KiboAgent:
    def __init__(self, config: AgentConfig, api_key: Optional[str] = None):
        kibo_core.init()
        
        self.service = DistributedWorkflowService()
        
        self.adapter = create_distributed_agent(config, api_key=api_key)
        
    def run(self, input_data: Any) -> AgentResult:
        """
        Synchronous execution. Submits and waits for result.
        """
        future = self.run_async(input_data)
        return future.result()

    def run_async(self, input_data: Any) -> KiboFuture:
        """
        Asynchronous execution. Returns a KiboFuture.
        """
        future = self.service.submit_agent_task(
            agent=self.adapter,
            input_data=input_data
        )
        return KiboFuture(future)

def create_agent(config: AgentConfig, api_key: Optional[str] = None) -> KiboAgent:
    """
    High-level factory to create a ready-to-use KiboAgent.
    Automatically initializes the Kibo runtime if needed.
    """
    return KiboAgent(config, api_key)
