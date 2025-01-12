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
        input_text = str(request.input_data)
        # Agno agents usually accept a message string
        response = self.agent.run(input_text)
        
        # Extract content
        content = response.content if hasattr(response, 'content') else str(response)

        # Safely extract model name to avoid pickling the whole model object (which has locks)
        model_obj = getattr(self.agent, "model", None)
        model_name = "unknown"
        if model_obj:
             # Try common attributes for model names in Agno/PhiData
             model_name = getattr(model_obj, "id", getattr(model_obj, "name", str(model_obj)))

        # Extract usage/metrics if available
        usage = {}
        if hasattr(response, 'metrics'):
            usage = response.metrics
        elif hasattr(response, 'usage'):
            usage = response.usage

        return AgentResult(
            output_data=content,
            metadata={
                "adapter": "AgnoAdapter",
                "model": str(model_name),
                "usage": usage
            }
        )

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        # Agno async support usually via .arun() if available
        # Fallback to sync run for now or check library capabilities
        return self.execute(request)
