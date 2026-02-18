from typing import Any, Optional
import kiboai
from kiboai.domain.blueprint import AgentConfig
from kiboai.application.workflow import DistributedWorkflowService
from kiboai.application.factory import create_distributed_agent
from kiboai.domain.entities import AgentResult


class KiboFuture:
    def __init__(self, future):
        self._future = future

    def result(self) -> AgentResult:
        """
        Blocking wait for the result.
        Returns the AgentResult object (containing output_data and metadata).
        """
        return kiboai.get(self._future)


class KiboAgent:
    def __init__(
        self,
        config: AgentConfig,
        api_key: Optional[str] = None,
        enable_distributed_execution: Optional[bool] = None,
        adapter: Optional[Any] = None,
    ):
        # Determine execution mode: Explicit Arg > Config > Default (False)
        self.is_distributed = (
            enable_distributed_execution
            if enable_distributed_execution is not None
            else config.distributed
        )

        kiboai.init(distributed_execution=self.is_distributed)

        self.service = DistributedWorkflowService(
            enable_distributed_execution=self.is_distributed
        )

        if adapter:
            self.adapter = adapter
        else:
            self.adapter = create_distributed_agent(config, api_key=api_key)

    def run(
        self,
        input_data: Any,
        distributed: Optional[bool] = None,
        params: Optional[dict] = None,
    ) -> AgentResult:
        """
        Synchronous execution. Submits and waits for result.
        :param distributed: Override execution mode for this run.
        :param params: Optional parameters for execution context (e.g. thread_id).
        """
        future = self.run_async(input_data, distributed=distributed, params=params)
        return future.result()

    def run_async(
        self,
        input_data: Any,
        distributed: Optional[bool] = None,
        params: Optional[dict] = None,
    ) -> KiboFuture:
        """
        Asynchronous execution. Returns a KiboFuture.
        :param distributed: Override execution mode for this run.
        :param params: Optional parameters for execution context.
        """
        future = self.service.submit_agent_task(
            agent=self.adapter,
            input_data=input_data,
            distributed=distributed,
            params=params,
        )
        return KiboFuture(future)


def create_agent(
    config: AgentConfig,
    api_key: Optional[str] = None,
    enable_distributed_execution: Optional[bool] = None,
    adapter: Optional[Any] = None,
) -> KiboAgent:
    """
    High-level factory to create a ready-to-use KiboAgent.
    Automatically initializes the Kibo runtime if needed.
    :param enable_distributed_execution: If True, uses Ray Cluster. If False, runs locally.
                                         If None, uses the setting from AgentConfig.

    :param adapter: Optional adapter instance. If provided, it overrides the default factory creation.
                    Useful for passing pre-configured graphs (LangGraph) or teams (CrewAI/Agno).
    """
    return KiboAgent(config, api_key, enable_distributed_execution, adapter=adapter)
