from typing import List, Any
from kiboai.domain.tools import KiboTool


def convert_tools(tools: List[Any], framework: str) -> List[Any]:
    """
    Converts a list of tools (which may contain KiboTools)
    to the format expected by the target framework.
    """
    converted = []
    for tool in tools:
        if isinstance(tool, KiboTool):
            converter = _get_converter(framework)
            if converter:
                converted.append(converter(tool))
            else:
                # Fallback: some frameworks usually take raw callables or we pass it as is
                # if we assume the user might have passed a compatible object by mistake
                converted.append(tool.func)
        else:
            converted.append(tool)
    return converted


def _get_converter(framework: str):
    if framework == "langchain":
        return _to_langchain
    elif framework == "crewai":
        return _to_crewai
    elif framework == "agno":
        return _to_agno
    elif framework == "pydantic_ai":
        return _to_pydantic_ai
    return None


def _to_langchain(tool: KiboTool):
    from langchain.tools import StructuredTool

    return StructuredTool.from_function(
        func=tool.func,
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
    )


def _to_crewai(tool: KiboTool):
    from crewai.tools import BaseTool

    # CrewAI accepts generic BaseTool subclasses.
    # We dynamically create a class or use LangChain tool (CrewAI supports LC tools)
    # Using LC tool wrapper is safest as it's fully supported by CrewAI
    return _to_langchain(tool)


def _to_agno(tool: KiboTool):
    from agno.utils.log import logger

    # Agno accepts instances of Toolkit or simple callables.
    # For a generic function, we can pass the function directly.
    # Agno inspects the function signature.

    # We should ensure the function has a proper name and docstring matching the tool
    f = tool.func
    f.__name__ = tool.name
    f.__doc__ = tool.description
    return f


def _to_pydantic_ai(tool: KiboTool):
    # PydanticAI accepts a list of functions.
    # We return the function directly.
    f = tool.func
    f.__name__ = tool.name
    f.__doc__ = tool.description
    return f
