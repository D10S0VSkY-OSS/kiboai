from uuid import uuid4
from kiboai.domain.entities import AgentRequest, AgentContext
from kiboai.domain.ports import IAgentNode

# Delayed import to avoid hard dependency on Ray
# from kiboai.infrastructure.executors.ray_executor import RayDistributedExecutor
# import ray

from kiboai.infrastructure.executors.local_executor import LocalExecutor


class DistributedWorkflowService:
    def __init__(self, enable_distributed_execution: bool = False):
        """
        Initializes the workflow engine (Dual Mode: Local & Distributed).
        :param enable_distributed_execution: Default execution mode.
        """
        self.default_distributed = enable_distributed_execution
        self._local_executor = None
        self._ray_executor = None

    @property
    def local_executor(self):
        if self._local_executor is None:
            self._local_executor = LocalExecutor()
        return self._local_executor

    @property
    def ray_executor(self):
        if self._ray_executor is None:
            try:
                from kiboai.infrastructure.executors.ray_executor import (
                    RayDistributedExecutor,
                )

                # Only connect to Ray when absolutely needed
                self._ray_executor = RayDistributedExecutor()
            except ImportError as e:
                raise ImportError(
                    "Ray is not installed. Please install 'kiboai[ray]' to use distributed execution."
                ) from e
        return self._ray_executor

    def _GetExecutor(self, distributed_override: bool = None):
        is_distributed = (
            distributed_override
            if distributed_override is not None
            else self.default_distributed
        )
        return (
            self.ray_executor if is_distributed else self.local_executor
        ), is_distributed

    def run_agent_task(
        self,
        agent: IAgentNode,
        input_data: str,
        params: dict = None,
        distributed: bool = None,
    ) -> str:
        """
        Runs an agent task. If distributed, waits for the result.
        """
        if params is None:
            params = {}

        executor, is_distributed = self._GetExecutor(distributed)

        context = AgentContext(workflow_id=uuid4(), step_id=uuid4(), params=params)
        request = AgentRequest(input_data=input_data, context=context)

        future = executor.execute_remote(agent, request)

        if is_distributed:
            import kiboai.infrastructure.runtime as runtime

            result = runtime.get(future)
        else:
            result = future.result()

        return result

    def submit_agent_task(
        self,
        agent: IAgentNode,
        input_data: str,
        params: dict = None,
        distributed: bool = None,
    ):
        """
        Submits an agent task.
        If distributed, returns a Ray ObjectRef (future).
        If local, returns a concurrent.futures.Future.
        """
        if params is None:
            params = {}

        executor, is_distributed = self._GetExecutor(distributed)

        context = AgentContext(workflow_id=uuid4(), step_id=uuid4(), params=params)
        request = AgentRequest(input_data=input_data, context=context)

        return executor.execute_remote(agent, request)

    def get_result(self, task_handle):
        """
        Retrieves the result from a task handle (Future or direct result).
        Unified method to handle both distributed (Ray ObjectRef) and local results.
        """
        import kiboai.infrastructure.runtime as runtime

        return runtime.get(task_handle)
        return task_handle
