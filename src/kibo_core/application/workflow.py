from uuid import uuid4
from kibo_core.domain.entities import AgentRequest, AgentContext
from kibo_core.domain.ports import IAgentNode
from kibo_core.infrastructure.executors.ray_executor import RayDistributedExecutor
import ray

class DistributedWorkflowService:
    def __init__(self):
        self.executor = RayDistributedExecutor()

    def run_agent_task(self, agent: IAgentNode, input_data: str, params: dict = None) -> str:
        """
        Runs an agent task distributedly via Ray.
        """
        if params is None:
            params = {}

        context = AgentContext(
            workflow_id=uuid4(),
            step_id=uuid4(),
            params=params
        )

        request = AgentRequest(
            input_data=input_data,
            context=context
        )

        future = self.executor.execute_remote(agent, request)
        
        result = ray.get(future)
        
        return result

    def submit_agent_task(self, agent: IAgentNode, input_data: str, params: dict = None):
        """
        Submits an agent task to Ray and returns the future (ObjectRef).
        Does not wait for completion.
        """
        if params is None:
            params = {}

        context = AgentContext(
            workflow_id=uuid4(),
            step_id=uuid4(),
            params=params
        )

        request = AgentRequest(
            input_data=input_data,
            context=context
        )

        future = self.executor.execute_remote(agent, request)
        
        return future
