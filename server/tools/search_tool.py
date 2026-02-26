"""
Web search tool using DuckDuckGo.
"""

import logging
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class SearchInput(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, description="Maximum number of results")


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Search the web for current information. "
        "Use this when you need up-to-date information or to answer "
        "questions about recent events."
    )
    args_schema: Type[BaseModel] = SearchInput

    async def _arun(self, query: str, max_results: int = 5) -> str:
        """Run web search and return formatted results."""
        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return f"No results found for: {query}"

            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(
                    f"{i}. **{r.get('title', 'N/A')}**\n"
                    f"   {r.get('body', 'N/A')}\n"
                    f"   Source: {r.get('href', 'N/A')}"
                )
            return "\n\n".join(formatted)

        except ImportError:
            return "Error: duckduckgo-search not installed"
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search error: {str(e)}"

    def _run(self, *args, **kwargs) -> str:
        return "Use async version (_arun)"
