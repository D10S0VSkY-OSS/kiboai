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
        inputs = request.input_data
        if not isinstance(inputs, dict):
            # Default to 'input' generic key, but keep 'topic' for backward compat or specific prompt templates
            inputs = {"input": str(inputs), "topic": str(inputs)}

        result = self.crew.kickoff(inputs=inputs)

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
                "model": model_name,
            },
        )

    async def aexecute(self, request: AgentRequest) -> AgentResult:
        inputs = request.input_data
        if not isinstance(inputs, dict):
            inputs = {"topic": str(inputs)}

        result = await self.crew.kickoff_async(inputs=inputs)

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
                "model": model_name,
            },
        )
