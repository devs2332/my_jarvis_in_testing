"""
Browser tools for web operations.

Provides functions to open URLs and search the web.
"""

import logging
import webbrowser
import requests
from bs4 import BeautifulSoup
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

def scrape_url(url: str):
    """
    Scrapes and extracts main text content from a URL.
    
    Args:
        url (str): URL to scrape
        
    Returns:
        str: Extracted text content or error message
        
    Example:
        >>> text = scrape_url("https://example.com")
        >>> print(text[:50])
        Example Domain
    """
    try:
        if not url.startswith("http"):
            url = "https://" + url
            
        logger.info(f"🕸️ Scraping URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        logger.info(f"✅ Scraped {len(text)} chars from {url}")
        return text[:10000] # Return first 10k chars to avoid token limits
        
    except Exception as e:
        logger.error(f"❌ Error scraping {url}: {e}")
        return f"Failed to scrape content from {url}: {str(e)}"
