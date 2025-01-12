from kibo_core.domain.ports import IAgentNode
from kibo_core.domain.entities import AgentRequest, AgentResult


class PydanticAIAdapter(IAgentNode):
    """
    Adapter for PydanticAI Agents.
    """

    def __init__(self, agent):
        self.agent = agent

    def execute(self, request: AgentRequest) -> AgentResult:
        input_text = str(request.input_data)

        result = self.agent.run_sync(input_text)

        return AgentResult(
            output_data=str(result.data),
            metadata={
                "adapter": "PydanticAIAdapter",
                "usage": result.usage() if hasattr(result, "usage") else {},
            },
        )

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        input_text = str(request.input_data)
        result = await self.agent.run(input_text)

        return AgentResult(
            output_data=str(result.data),
            metadata={
                "adapter": "PydanticAIAdapter",
                "usage": result.usage() if hasattr(result, "usage") else {},
            },
        )
