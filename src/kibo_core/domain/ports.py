from typing import Protocol, runtime_checkable
from .entities import AgentRequest, AgentResult

@runtime_checkable
class IAgentNode(Protocol):
    """
    Port (Interface) that all Agent Adapters must implement.
    This separates the domain from specific libraries like LangGraph or CrewAI.
    """
    def execute(self, request: AgentRequest) -> AgentResult:
        """
        Execute the agent logic synchronously.
        """
        ...

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        """
        Execute the agent logic asynchronously.
        """
        ...
