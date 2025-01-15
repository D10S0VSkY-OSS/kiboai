from typing import Any, Dict
from kibo_core.domain.ports import IAgentNode
from kibo_core.domain.entities import AgentRequest, AgentResult
from crewai import Crew

class CrewAIAdapter(IAgentNode):
    """
    Adapter for CrewAI assignments.
    """
    def __init__(self, crew: Crew):
        self.crew = crew

    def execute(self, request: AgentRequest) -> AgentResult:
        # CrewAI expects a dict of inputs usually
        inputs = request.input_data
        if not isinstance(inputs, dict):
            # Try to infer or wrap if string
            inputs = {"topic": str(inputs)}
            
        result = self.crew.kickoff(inputs=inputs)
        
        # CrewAI result is a CrewOutput object.
        
        # Try to extract model from the first agent if available
        model_name = "unknown"
        if self.crew.agents and hasattr(self.crew.agents[0], "llm"):
             # CrewAI Agent -> LLM entity
             llm = self.crew.agents[0].llm
             if hasattr(llm, "model"):
                 model_name = llm.model
        
        return AgentResult(
            output_data=result.raw,
            request_id=request.request_id,
            metadata={
                "adapter": "CrewAIAdapter",
                "token_usage": getattr(result, "token_usage", {}),
                "model": model_name
            }
        )

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        # CrewAI async support is via kickoff_async since v0.x
        inputs = request.input_data
        if not isinstance(inputs, dict):
            inputs = {"topic": str(inputs)}
            
        result = await self.crew.kickoff_async(inputs=inputs)

        # Describe Model
        model_name = "unknown"
        if self.crew.agents and hasattr(self.crew.agents[0], "llm"):
             llm = self.crew.agents[0].llm
             if hasattr(llm, "model"):
                 model_name = llm.model
        
        return AgentResult(
            output_data=result.raw,
            request_id=request.request_id,
            metadata={
                "adapter": "CrewAIAdapter",
                "token_usage": getattr(result, "token_usage", {}),
                "model": model_name
            }
        )
