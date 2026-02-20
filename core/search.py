"""
Internet search functionality using DuckDuckGo.

Provides web search capabilities without requiring API keys.
"""

import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)


class InternetSearch:
    """
    Web search engine using DuckDuckGo.
    
    Provides anonymous web search without requiring API authentication.
    """
    
    def __init__(self):
        """Initialize the search engine."""
        logger.info("Internet search initialized (DuckDuckGo)")
    
    def search(self, query, max_results=5):
        """
        Search the web for information.
        
        Args:
            query (str): Search query string
            max_results (int): Maximum number of results to return (default: 5)
            
        Returns:
            list: List of dictionaries containing search results with 'title' and 'body' keys
            
        Example:
            >>> search = InternetSearch()
            >>> results = search.search("Python programming", max_results=3)
        """
        results = []
        
        try:
            logger.info(f"🔍 Searching web: '{query}' (max: {max_results} results)")
            
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "href": r.get("href", r.get("link", "")) # Capture URL for scraping
                    })
            
            logger.info(f"✅ Found {len(results)} search results")
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            # Return empty results on error instead of crashing
            results = []
        
        return results
