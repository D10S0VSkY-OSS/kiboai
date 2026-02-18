from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


@dataclass
class AgentContext:
    """
    Rich context passed to agents.
    'params' allows passing framework-specific configurations
    (e.g., {'recursion_limit': 10} for LangGraph, {'process': 'sequential'} for CrewAI).
    """

    workflow_id: UUID
    step_id: UUID
    history: list[Dict[str, Any]] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRequest:
    """
    A request to execute an agent's logic.
    """

    input_data: Any
    context: AgentContext
    request_id: UUID = field(default_factory=uuid4)


@dataclass
class AgentResult:
    """
    The result produced by an agent.
    """

    output_data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[UUID] = None
