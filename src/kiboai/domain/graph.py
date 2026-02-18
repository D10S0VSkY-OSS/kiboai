from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from kiboai.domain.blueprint import AgentConfig

# Constants for Graph flow
START = "__start__"
END = "__end__"


class Node(BaseModel):
    """Represents a processing node in the graph."""

    id: str
    agent: Optional[AgentConfig] = None
    function: Optional[Callable] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_runnable(self):
        """Returns the executable logic for this node."""
        if self.function:
            return self.function
        # If agent, we'll need to wrap it into a callable that runs the agent
        # This part will be handled by the compiler
        return None


class Edge(BaseModel):
    """Represents a connection between nodes."""

    source: str
    target: str
    condition: Optional[Callable] = None  # For conditional edges


class KiboGraph(BaseModel):
    """
    Declarative definition of a processing graph.
    Abstracts away specific implementation details (e.g., LangGraph StateGraph).
    """

    name: str
    nodes: Dict[str, Node] = Field(default_factory=dict)
    edges: List[Edge] = Field(default_factory=list)
    state_schema: Optional[Any] = None  # Type/Class for the state
    entry_point: Optional[str] = None

    def add_node(
        self,
        id: str,
        agent: Optional[AgentConfig] = None,
        function: Optional[Callable] = None,
    ):
        if not agent and not function:
            raise ValueError("Node must have either an agent or a function.")
        self.nodes[id] = Node(id=id, agent=agent, function=function)

    def add_edge(self, source: str, target: str, condition: Optional[Callable] = None):
        if source != START and source not in self.nodes:
            raise ValueError(f"Source node '{source}' not found in graph.")
        if target != END and target not in self.nodes:
            raise ValueError(f"Target node '{target}' not found in graph.")
        self.edges.append(Edge(source=source, target=target, condition=condition))

    def set_entry_point(self, node_id: str):
        if node_id not in self.nodes:
            raise ValueError(f"Entry point '{node_id}' not found.")
        self.entry_point = node_id

    def compile(self) -> Any:
        # This will need to dynamically load the compiler implementation
        # to avoid circular dependencies.
        from kiboai.infrastructure.graph_compiler import compile_graph

        return compile_graph(self)
