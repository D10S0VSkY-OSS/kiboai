from typing import Optional
import os
from kiboai.domain.tools import KiboTool


def _tavily_search(query: str, api_key: str = None) -> str:
    from tavily import TavilyClient

    api_key = api_key or os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not found."

    try:
        client = TavilyClient(api_key=api_key)
        return str(client.search(query, search_depth="basic"))
    except Exception as e:
        return f"Search failed: {str(e)}"


class TavilySearchTool(KiboTool):
    """
    Standard Kibo Tool for web search using Tavily.
    """

    def __init__(self, api_key: Optional[str] = None):
        # Create a closure or partial if needed, but here we keep it simple
        # We need to bind the api_key if provided

        def search_func(query: str):
            return _tavily_search(query, api_key=api_key)

        super().__init__(
            name="web_search",
            description="Search the web for current information.",
            func=search_func,
        )
