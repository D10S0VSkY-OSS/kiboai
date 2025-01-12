from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class AgentConfig(BaseModel):
    """
    Universal definition of an AI Agent in Kibo.
    Designed for high DX execution, independent of the underlying engine.
    """
    
    name: str = Field(..., description="Unique name/ID of the agent")
    description: str = Field(..., description="Role, backstory, or identity of the agent. Who it is.")
    
    instructions: str = Field(..., description="Goal, system prompt, or specific instructions for behavior.")
    
    agent: str = Field("crewai", description="The underlying engine to use: 'crewai', 'agno', 'langchain', 'pydantic_ai'")
    model: str = Field("gpt-4o-mini", description="The LLM model ID to use.")
    
    config: Dict[str, Any] = Field(default_factory=dict, description="Engine-specific configuration.")

    model_config = ConfigDict(extra="allow")

    def run(self, input_data: Any) -> Any:
        """
        Syntactic sugar to execute this blueprint immediately via Kibo.
        """
        pass
