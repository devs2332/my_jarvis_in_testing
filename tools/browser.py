"""
Browser tools for web operations.

Provides functions to open URLs and search the web.
"""

import logging
import webbrowser
from ddgs import DDGS

logger = logging.getLogger(__name__)


def open_url(url: str):
    """
    Opens a URL in the default browser.
    
    Args:
        url (str): URL to open (automatically adds https:// if missing)
        
    Returns:
        str: Success message
        
    Example:
        >>> open_url("google.com")
        'Opened https://google.com'
    """
    try:
        if not url.startswith("http"):
            url = "https://" + url
        
        logger.info(f"🌍 Opening URL: {url}")
        webbrowser.open(url)
        return f"Opened {url}"
        
    except Exception as e:
        logger.error(f"❌ Error opening URL {url}: {e}")
        return f"Failed to open {url}: {str(e)}"


def search_google(query: str):
    """
    Searches Google and opens the first result.
    
    Args:
        query (str): Search query string
        
    Returns:
        str: Success message
        
    Example:
        >>> search_google("Python programming")
        'Searched for Python programming'
    """
    try:
        logger.info(f"🔍 Searching Google: '{query}'")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searched for {query}"
        
    except Exception as e:
        logger.error(f"❌ Error searching Google: {e}")
        return f"Failed to search: {str(e)}"


def get_search_results(query: str, max_results=5):
    """
    Returns raw search results for the brain to process.
    
    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return (default: 5)
        
    Returns:
        list: List of search result dictionaries
        
    Example:
        >>> results = get_search_results("Python", max_results=3)
        >>> print(len(results))
        3
    """
    results = []
    
    try:
        logger.info(f"🔍 Getting search results for: '{query}'")
        
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(r)
        
        logger.info(f"✅ Retrieved {len(results)} search results")
        
    except Exception as e:
        logger.error(f"❌ Error getting search results: {e}")
        
    return results
