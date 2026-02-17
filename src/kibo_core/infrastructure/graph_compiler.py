import operator
from typing import Annotated, Any, Callable, Dict, List, Optional, TypedDict, Union

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import RunnableLambda

try:
    from langgraph.graph import END as LG_END
    from langgraph.graph import START as LG_START
    from langgraph.graph import StateGraph
except ImportError:
    StateGraph = None
    LG_START = None
    LG_END = None

from kibo_core.domain.blueprint import AgentConfig
from kibo_core.domain.graph import END, START, KiboGraph, Node
from kibo_core.infrastructure.adapters.langgraph_adapter import LangGraphAdapter
from kibo_core.infrastructure.interfaces.client import create_agent


class Wrapper:
    """Helper class to wrap callables or agents into something LangGraph can execute."""

    @staticmethod
    def create_runner(node: Node, api_key: Optional[str] = None):
        if node.function:
            return RunnableLambda(node.function)

        if node.agent:
            # Create the agent instance using Kibo's factory
            # Note: This creates a fresh agent instance for each execution if compiled here.
            # In a real heavy scenario, we might want to cache or pass the instance.
            agent_instance = create_agent(node.agent, api_key=api_key)

            def agent_runner(state: Dict):
                # LangGraph passes 'state' as input (dict or TypedDict).
                # We extract the input string for the agent.
                input_text = ""
                if isinstance(state, dict):
                    msgs = state.get("messages", [])
                    if msgs:
                        last_msg = msgs[-1]
                        # Handling LangChain Message object or tuple
                        if hasattr(last_msg, "content"):
                            input_text = last_msg.content
                        elif isinstance(last_msg, tuple):
                            input_text = last_msg[1]
                        else:
                            input_text = str(last_msg)
                    else:
                        # Fallback for states without messages key
                        # Maybe 'topic' or 'input' key?
                        for key in ["input", "topic", "query"]:
                            if key in state:
                                input_text = str(state[key])
                                break
                        if not input_text:
                            input_text = str(state)
                else:
                    input_text = str(state)

                # Run Kibo Agent
                # TODO: Support async if needed
                result = agent_instance.run(input_text)

                # Format output back to LangGraph expected state update
                # We assume the default state has 'messages' key for append
                # If the state schema is custom, this might need adjustment.
                return {"messages": [AIMessage(content=result.output_data)]}

            return RunnableLambda(agent_runner)

        raise ValueError(f"Node '{node.id}' has no executable logic defined.")


def compile_graph(graph: KiboGraph, api_key: Optional[str] = None) -> LangGraphAdapter:
    """Compiles a KiboGraph definition into an executable LangGraph app."""
    if StateGraph is None:
        raise ImportError("LangGraph is not installed. Please install langgraph.")

    # 1. Define State Schema
    builder = None
    if graph.state_schema:
        builder = StateGraph(graph.state_schema)
    else:
        # Default state schema if none provided: List of Messages
        class DefaultState(TypedDict):
            messages: Annotated[List[BaseMessage], operator.add]

        builder = StateGraph(DefaultState)

    # 2. Add Nodes
    for node_id, node in graph.nodes.items():
        runner = Wrapper.create_runner(node, api_key=api_key)
        builder.add_node(node_id, runner)

    # 3. Add Edges
    # Handle Entry Point
    if graph.entry_point:
        builder.add_edge(LG_START, graph.entry_point)
    else:
        # Infer entry point from first edge starting at START
        start_edges = [e for e in graph.edges if e.source == START]
        if start_edges:
            builder.add_edge(LG_START, start_edges[0].target)
        elif graph.nodes:
            # Fallback: prompt first node added
            first_node_id = next(iter(graph.nodes))
            builder.add_edge(LG_START, first_node_id)

    for edge in graph.edges:
        if edge.source == START:
            continue  # Handled above

        target = edge.target
        if target == END:
            target = LG_END

        if edge.condition:
            builder.add_conditional_edges(
                edge.source,
                edge.condition,
                # Simple mapping: condition result -> target node
                # Or mapping dict if edge.target is a dict
                edge.target if isinstance(edge.target, dict) else {True: edge.target},
            )
        else:
            builder.add_edge(edge.source, target)

    # 4. Compile
    app = builder.compile()

    # 5. Return wrapped Adapter
    return LangGraphAdapter(app)
