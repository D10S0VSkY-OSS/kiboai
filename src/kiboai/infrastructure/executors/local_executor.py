from typing import Any
from kiboai.domain.ports import IAgentNode
from kiboai.domain.entities import AgentRequest, AgentResult


class LocalExecutor:
    """
    Executes agents locally in the current process.
    """

    def __init__(self):
        from concurrent.futures import ThreadPoolExecutor

        self._executor = ThreadPoolExecutor()

    def execute_remote(self, agent_adapter: IAgentNode, request: AgentRequest) -> Any:
        # Offload execution to a thread to avoid blocking the event loop
        # and to provide a clean environment for libraries that use asyncio.run()
        return self._executor.submit(agent_adapter.execute, request)
