from typing import Any
from kibo_core.domain.ports import IAgentNode
from kibo_core.domain.entities import AgentRequest, AgentResult


class AgnoAdapter(IAgentNode):
    """
    Adapter for Agno (formerly PhiData) Agents.
    """

    def __init__(self, agent):
        self.agent = agent

    def execute(self, request: AgentRequest) -> AgentResult:
        print("[AgnoAdapter] Starting execution...")
        input_text = str(request.input_data)
        response = self.agent.run(input_text, stream=False)
        print("[AgnoAdapter] Execution finished.")

        content = response.content if hasattr(response, "content") else str(response)

        model_obj = getattr(self.agent, "model", None)
        model_name = "unknown"
        if model_obj:
            model_name = getattr(
                model_obj, "id", getattr(model_obj, "name", str(model_obj))
            )

        usage = {}
        if hasattr(response, "metrics"):
            usage = response.metrics
        elif hasattr(response, "usage"):
            usage = response.usage

        return AgentResult(
            output_data=content,
            metadata={
                "adapter": "AgnoAdapter",
                "model": str(model_name),
                "usage": usage,
            },
        )

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        return self.execute(request)
