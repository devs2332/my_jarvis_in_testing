"""
Google Dorking Query Transformer.

Detects user query intent and rewrites queries with advanced search
operators (site:, intitle:, filetype:, "exact phrase", exclusions,
recency filters) for dramatically more accurate search results.
"""

import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Site mappings per intent category ──────────────────────────
SITE_MAPS = {
    "coding": [
        "site:stackoverflow.com",
        "site:github.com",
        "site:dev.to",
    ],
    "academic": [
        "site:arxiv.org",
        "site:scholar.google.com",
        "site:researchgate.net",
    ],
    "news": [
        "site:reuters.com OR site:bbc.com OR site:theverge.com",
    ],
    "opinion": [
        "site:reddit.com",
    ],
    "docs": [
        "site:docs.python.org OR site:developer.mozilla.org OR site:learn.microsoft.com",
    ],
    "security": [
        "site:cve.mitre.org OR site:nvd.nist.gov OR site:exploit-db.com",
    ],
}

# ── Noise domains to exclude from technical queries ───────────
NOISE_EXCLUSIONS = "-pinterest -quora -tiktok -instagram"

# ── Intent detection keyword sets ─────────────────────────────
INTENT_KEYWORDS = {
    "coding": [
        "error", "exception", "traceback", "bug", "fix", "debug",
        "code", "function", "class", "import", "module", "library",
        "python", "javascript", "java", "c++", "rust", "golang",
        "react", "django", "flask", "node", "npm", "pip",
        "stackoverflow", "github", "api", "sdk",
    ],
    "academic": [
        "research", "paper", "study", "journal", "thesis",
        "whitepaper", "citation", "peer-reviewed", "abstract",
        "methodology", "hypothesis", "experiment", "analysis",
        "pdf", "arxiv", "ieee", "acm",
    ],
    "news": [
        "news", "latest", "today", "yesterday", "breaking",
        "announced", "released", "launched", "update", "2026",
        "2025", "recent", "this week", "this month",
    ],
    "tutorial": [
        "how to", "tutorial", "guide", "step by step", "learn",
        "beginner", "getting started", "walkthrough", "course",
        "example", "setup", "install", "configure",
    ],
    "comparison": [
        "vs", "versus", "compared to", "better than", "difference between",
        "alternative to", "pros and cons", "which is better",
        "comparison", "benchmark",
    ],
    "opinion": [
        "reddit", "review", "opinion", "experience", "worth it",
        "should i", "recommend", "best", "top",
    ],
    "definition": [
        "what is", "what are", "define", "meaning of", "definition",
        "explain", "eli5",
    ],
    "security": [
        "cve", "vulnerability", "exploit", "malware", "ransomware",
        "cybersecurity", "pentest", "penetration testing", "hack",
        "threat", "zero-day", "patch",
    ],
    "download": [
        "download", "installer", "setup.exe", "release", "binary",
        "package", "filetype",
    ],
}


class QueryDorker:
    """
    Transforms natural-language user queries into dorked search queries
    using Google-style search operators for more accurate results.

    Supports single-query mode (web_search) and multi-query mode
    (deep_research) that produces several complementary dorked queries.
    """

    def __init__(self):
        self._current_year = datetime.now().year
        logger.info("QueryDorker initialized")

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def dork(self, query: str, mode: str = "web_search") -> list[str]:
        """
        Transform a user query into one or more dorked search queries.

        Args:
            query: Raw natural-language query from the user.
            mode:  'web_search'    → returns 1 optimised query
                   'deep_research' → returns up to 3 complementary queries

        Returns:
            List of dorked query strings (always at least one).
        """
        if not query or not query.strip():
            return [query]

        query = query.strip()
        intent = self._detect_intent(query)
        logger.info(f"🎯 Detected intent: {intent} for query: '{query[:60]}...'")

        if mode == "deep_research":
            queries = self._build_deep_queries(query, intent)
        else:
            queries = [self._build_single_query(query, intent)]

        logger.info(f"🔎 Dorked queries ({len(queries)}): {queries}")
        return queries

    # ──────────────────────────────────────────────
    # Intent detection
    # ──────────────────────────────────────────────

    def _detect_intent(self, query: str) -> str:
        """Classify a query into an intent category by keyword scoring."""
        query_lower = query.lower()
        scores: dict[str, int] = {}

        for intent, keywords in INTENT_KEYWORDS.items():
            score = 0
            for kw in keywords:
                # Use word-boundary matching to avoid false positives
                # e.g. "api" should NOT match inside "capital"
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, query_lower):
                    score += 1
            if score > 0:
                scores[intent] = score

        if not scores:
            return "general"

        return max(scores, key=scores.get)

    # ──────────────────────────────────────────────
    # Single-query builder (web_search mode)
    # ──────────────────────────────────────────────

    def _build_single_query(self, query: str, intent: str) -> str:
        """Build one optimised dorked query."""
        parts: list[str] = []

        # 1. Extract and quote key phrases
        core_query = self._extract_quoted_phrases(query)
        parts.append(core_query)

        # 2. Add site operators for known intents
        site_ops = self._get_site_operators(intent)
        if site_ops:
            parts.append(site_ops)

        # 3. Add intitle: for definitions / specific lookups
        if intent in ("definition", "tutorial"):
            keyword = self._extract_main_keyword(query)
            if keyword:
                parts.append(f'intitle:"{keyword}"')

        # 4. Add filetype: for academic / download queries
        if intent == "academic":
            parts.append("filetype:pdf")
        elif intent == "download":
            parts.append("filetype:exe OR filetype:msi OR filetype:zip")

        # 5. Add recency for news queries
        if intent == "news":
            parts.append(f"after:{self._current_year - 1}")

        # 6. Exclude noise sites for technical queries
        if intent in ("coding", "tutorial", "academic", "security"):
            parts.append(NOISE_EXCLUSIONS)

        return " ".join(parts)

    # ──────────────────────────────────────────────
    # Multi-query builder (deep_research mode)
    # ──────────────────────────────────────────────

    def _build_deep_queries(self, query: str, intent: str) -> list[str]:
        """
        Build 2-3 complementary dorked queries for deep research.

        Strategy:
          Q1 — primary dorked query (same as web_search)
          Q2 — site-specific deep dive (authoritative source)
          Q3 — broad perspective / community angle
        """
        queries = []

        # Q1: Primary dorked query
        q1 = self._build_single_query(query, intent)
        queries.append(q1)

        # Q2: Authoritative / academic angle
        core = self._extract_quoted_phrases(query)
        if intent == "coding":
            queries.append(f"{core} site:github.com OR site:docs.python.org {NOISE_EXCLUSIONS}")
        elif intent == "security":
            queries.append(f"{core} site:cve.mitre.org OR site:exploit-db.com")
        elif intent == "academic":
            queries.append(f"{core} site:arxiv.org OR site:scholar.google.com filetype:pdf")
        elif intent == "news":
            queries.append(f"{core} site:reuters.com OR site:apnews.com after:{self._current_year}")
        else:
            # General authoritative lookup
            queries.append(f"{core} site:wikipedia.org OR site:britannica.com")

        # Q3: Community / real-world perspective
        if intent not in ("academic", "news"):
            queries.append(f"{core} site:reddit.com OR site:news.ycombinator.com")

        return queries[:3]   # Cap at 3

    # ──────────────────────────────────────────────
    # Helper utilities
    # ──────────────────────────────────────────────

    def _extract_quoted_phrases(self, query: str) -> str:
        """
        Identify potential multi-word key phrases in the query and
        wrap them in exact-match quotes.

        Heuristic: if the query contains a recognisable noun phrase
        of 2-4 words, quote it.  Otherwise return query as-is.
        """
        # If user already used quotes, leave them
        if '"' in query:
            return query

        # Remove common question prefixes
        cleaned = re.sub(
            r"^(what is|what are|how to|how do i|explain|define|tell me about|search for|find)\s+",
            "",
            query,
            flags=re.IGNORECASE,
        ).strip()

        # If the cleaned core is 2-4 words, exact-quote it
        words = cleaned.split()
        if 2 <= len(words) <= 4:
            return f'"{cleaned}"'

        # For longer queries, try to quote the first meaningful 2-3 word chunk
        if len(words) > 4:
            # Quote the first 3 words as the key phrase, keep the rest
            key_phrase = " ".join(words[:3])
            remainder = " ".join(words[3:])
            return f'"{key_phrase}" {remainder}'

        return cleaned if cleaned else query

    def _extract_main_keyword(self, query: str) -> str:
        """Pull the single most important keyword from the query."""
        # Remove stopwords and return the longest remaining word
        stopwords = {
            "what", "is", "are", "how", "to", "do", "i", "the", "a", "an",
            "in", "on", "at", "for", "of", "and", "or", "with", "about",
            "this", "that", "it", "my", "me", "can", "should", "best",
            "tell", "explain", "find", "search", "get", "show", "please",
        }
        words = [w for w in query.lower().split() if w not in stopwords]
        if not words:
            return ""
        return max(words, key=len)

    def _get_site_operators(self, intent: str) -> str:
        """Return site: operator string for a given intent, or empty."""
        sites = SITE_MAPS.get(intent, [])
        if not sites:
            return ""
        # Use the first mapping (already may contain OR)
        return sites[0]
