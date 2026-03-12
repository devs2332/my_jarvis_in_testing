"""
Internet search functionality using DuckDuckGo.

Provides web search capabilities without requiring API keys.
Supports both single-query and multi-query (dorked) search modes.
"""

import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)


class InternetSearch:
    """
    Web search engine using DuckDuckGo.

    Provides anonymous web search without requiring API authentication.
    Supports multi-query dorked search with deduplication.
    """

    def __init__(self):
        """Initialize the search engine."""
        logger.info("Internet search initialized (DuckDuckGo)")

    def search(self, query, max_results=5):
        """
        Search the web for information (single query).

        Args:
            query (str): Search query string
            max_results (int): Maximum number of results to return (default: 5)

        Returns:
            list: List of dicts with 'title', 'body', and 'href' keys
        """
        results = []

        try:
            logger.info(f"🔍 Searching web: '{query}' (max: {max_results} results)")

            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "href": r.get("href", r.get("link", ""))
                    })

            logger.info(f"✅ Found {len(results)} search results")

        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            results = []

        return results

    def search_multiple(self, queries, max_results_per_query=5):
        """
        Run multiple dorked queries and merge results, deduplicating by URL.

        Args:
            queries (list[str]): List of search query strings (dorked)
            max_results_per_query (int): Max results per individual query

        Returns:
            list: Deduplicated list of search result dicts
        """
        seen_urls = set()
        merged = []

        for query in queries:
            hits = self.search(query, max_results=max_results_per_query)
            for hit in hits:
                url = hit.get("href", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    merged.append(hit)
                elif not url:
                    # Keep results without URLs (rare edge case)
                    merged.append(hit)

        logger.info(
            f"🔎 Multi-query search: {len(queries)} queries → "
            f"{len(merged)} unique results"
        )
        return merged
