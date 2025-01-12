from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class AgentConfig(BaseModel):
    """
    Universal definition of an AI Agent in Kibo.
    Designed for high DX execution, independent of the underlying engine.
    """
    
    # --- 1. CORE IDENTITY (Who am I?) ---
    name: str = Field(..., description="Unique name/ID of the agent")
    description: str = Field(..., description="Role, backstory, or identity of the agent. Who it is.")
    
    # --- 2. CORE INTENT (What do I do?) ---
    instructions: str = Field(..., description="Goal, system prompt, or specific instructions for behavior.")
    
    # --- 3. ENGINE CONFIG (How do I run?) ---
    agent: str = Field("crewai", description="The underlying engine to use: 'crewai', 'agno', 'langchain', 'pydantic_ai'")
    model: str = Field("gpt-4o-mini", description="The LLM model ID to use.")
    
    # --- 4. EXTENSIBILITY (Advanced Stuff) ---
    # Flexible container for engine-specific parameters (e.g., 'temperature', 'verbose', 'tools')
    config: Dict[str, Any] = Field(default_factory=dict, description="Engine-specific configuration.")

    model_config = ConfigDict(extra="allow")

    def run(self, input_data: Any) -> Any:
        """
        Syntactic sugar to execute this blueprint immediately via Kibo.
        """
        # This will be linked to the runtime later to allow:
        # my_agent = AgentBlueprint(...)
        # result = my_agent.run("do something")
        pass
