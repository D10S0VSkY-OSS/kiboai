from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, Field
from kiboai.domain.blueprint import AgentConfig


class WorkflowStep(BaseModel):
    id: str = Field(..., description="Unique identifier for this step.")
    agent: AgentConfig = Field(
        ..., description="Configuration of the agent executing this step."
    )
    instruction: str = Field(..., description="Specific instruction for this step.")
    next: Optional[Union[str, List[str]]] = Field(
        None, description="ID(s) of the next step(s). None means end."
    )


class WorkflowConfig(BaseModel):
    """
    Declarative definition of a multi-agent workflow.
    """

    name: str = Field(..., description="Name of the workflow.")
    description: str = Field(..., description="Description of the workflow's purpose.")
    engine: str = Field(
        "langgraph",
        description="The underlying execution engine: 'langgraph', 'crewai', 'agno'.",
    )
    start_step: str = Field(..., description="ID of the starting step.")
    steps: List[WorkflowStep] = Field(..., description="List of steps in the workflow.")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Engine-specific configuration."
    )

    # Strat 1: Native extensions (Pass-through config)
    native_extensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary containing native objects or advanced configs passed directly to the engine's compiler/constructor.",
    )

    # Strat 2: Hooks (Callback)
    on_before_compile: Optional[Any] = Field(
        None,
        description="Optional callable/function that receives the builder/tasks list before final compilation. Allows native modification.",
    )
