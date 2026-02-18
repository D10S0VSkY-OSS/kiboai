from typing import Any
from kiboai.domain.ports import IAgentNode
from kiboai.domain.entities import AgentRequest, AgentResult


class BaseAgentAdapter(IAgentNode):
    """
    Base class for specific framework adapters.
    """

    def execute(self, request: AgentRequest) -> AgentResult:
        raise NotImplementedError

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        raise NotImplementedError


class MockEchoAgentAdapter(BaseAgentAdapter):
    """
    Simple adapter for testing. Returns the input as output.
    """

    def execute(self, request: AgentRequest) -> AgentResult:
        input_text = str(request.input_data)

        prefix = request.context.params.get("echo_prefix", "Echo: ")

        output = f"{prefix}{input_text}"

        return AgentResult(
            output_data=output,
            metadata={"processed_by": "MockEchoAgentAdapter", "node": "local"},
        )

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        return self.execute(request)


class LazyAgentAdapter(BaseAgentAdapter):
    """
    Wraps an agent factory to defer initialization until execution.
    Useful for distributed execution where the agent itself (e.g. holding locks) cannot be pickled.
    """

    def __init__(self, factory_func, *args, **kwargs):
        self.factory_func = factory_func
        self.args = args
        self.kwargs = kwargs
        self._adapter = None

    def _get_adapter(self) -> IAgentNode:
        if self._adapter is None:
            self._adapter = self.factory_func(*self.args, **self.kwargs)
        return self._adapter

    def execute(self, request: AgentRequest) -> AgentResult:
        return self._get_adapter().execute(request)

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        return await self._get_adapter().aexecute(request)
