"""
Unit tests for the Google Dorking query transformer.

Tests intent detection, single-query dorking, and multi-query
deep-research expansion.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.google_dorking import QueryDorker


dorker = QueryDorker()


# ────────────────────────────────────────────────
# Intent detection
# ────────────────────────────────────────────────

def test_coding_intent():
    intent = dorker._detect_intent("python import error module not found")
    assert intent == "coding", f"Expected 'coding', got '{intent}'"
    print("✅ coding intent detected")


def test_news_intent():
    intent = dorker._detect_intent("latest AI news today 2026")
    assert intent == "news", f"Expected 'news', got '{intent}'"
    print("✅ news intent detected")


def test_academic_intent():
    intent = dorker._detect_intent("research paper on neural networks arxiv")
    assert intent == "academic", f"Expected 'academic', got '{intent}'"
    print("✅ academic intent detected")


def test_tutorial_intent():
    intent = dorker._detect_intent("how to setup django step by step beginner guide")
    assert intent == "tutorial", f"Expected 'tutorial', got '{intent}'"
    print("✅ tutorial intent detected")


def test_comparison_intent():
    intent = dorker._detect_intent("React vs Vue which is better for beginners")
    assert intent == "comparison", f"Expected 'comparison', got '{intent}'"
    print("✅ comparison intent detected")


def test_opinion_intent():
    intent = dorker._detect_intent("is tailwindcss worth it reddit review")
    assert intent == "opinion", f"Expected 'opinion', got '{intent}'"
    print("✅ opinion intent detected")


def test_security_intent():
    intent = dorker._detect_intent("CVE-2024-1234 vulnerability exploit details")
    assert intent == "security", f"Expected 'security', got '{intent}'"
    print("✅ security intent detected")


def test_general_intent():
    intent = dorker._detect_intent("capital of France")
    assert intent == "general", f"Expected 'general', got '{intent}'"
    print("✅ general intent for generic query")


# ────────────────────────────────────────────────
# Single-query dorking (web_search mode)
# ────────────────────────────────────────────────

def test_web_search_coding():
    queries = dorker.dork("python traceback import error", mode="web_search")
    assert len(queries) == 1
    q = queries[0]
    assert "site:stackoverflow.com" in q
    assert "-pinterest" in q
    print(f"✅ web_search coding: {q}")


def test_web_search_academic():
    queries = dorker.dork("research paper on transformers", mode="web_search")
    assert len(queries) == 1
    q = queries[0]
    assert "filetype:pdf" in q
    print(f"✅ web_search academic: {q}")


def test_web_search_news():
    queries = dorker.dork("latest tech news today", mode="web_search")
    assert len(queries) == 1
    q = queries[0]
    assert "after:" in q
    print(f"✅ web_search news: {q}")


def test_web_search_general():
    """General queries should still produce a valid query."""
    queries = dorker.dork("capital of France", mode="web_search")
    assert len(queries) == 1
    assert queries[0].strip() != ""
    print(f"✅ web_search general: {queries[0]}")


def test_web_search_empty():
    """Empty query should return as-is."""
    queries = dorker.dork("", mode="web_search")
    assert queries == [""]
    print("✅ empty query handled")


# ────────────────────────────────────────────────
# Multi-query dorking (deep_research mode)
# ────────────────────────────────────────────────

def test_deep_research_coding():
    queries = dorker.dork("python async await best practices", mode="deep_research")
    assert 2 <= len(queries) <= 3, f"Expected 2-3 queries, got {len(queries)}"
    # Q2 should target authoritative sources
    assert any("github.com" in q or "docs.python.org" in q for q in queries)
    print(f"✅ deep_research coding ({len(queries)} queries)")
    for i, q in enumerate(queries):
        print(f"   Q{i+1}: {q}")


def test_deep_research_news():
    queries = dorker.dork("latest AI breakthroughs 2026", mode="deep_research")
    assert 2 <= len(queries) <= 3
    assert any("reuters.com" in q or "apnews.com" in q for q in queries)
    print(f"✅ deep_research news ({len(queries)} queries)")


def test_deep_research_general():
    queries = dorker.dork("meaning of life", mode="deep_research")
    assert 2 <= len(queries) <= 3
    assert any("wikipedia.org" in q for q in queries)
    print(f"✅ deep_research general ({len(queries)} queries)")


# ────────────────────────────────────────────────
# Already-dorked queries
# ────────────────────────────────────────────────

def test_already_quoted():
    """User query that already has quotes should preserve them."""
    queries = dorker.dork('"machine learning" site:arxiv.org', mode="web_search")
    assert len(queries) == 1
    assert '"machine learning"' in queries[0]
    print(f"✅ already-quoted preserved: {queries[0]}")


# ────────────────────────────────────────────────
# Run all tests
# ────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_coding_intent,
        test_news_intent,
        test_academic_intent,
        test_tutorial_intent,
        test_comparison_intent,
        test_opinion_intent,
        test_security_intent,
        test_general_intent,
        test_web_search_coding,
        test_web_search_academic,
        test_web_search_news,
        test_web_search_general,
        test_web_search_empty,
        test_deep_research_coding,
        test_deep_research_news,
        test_deep_research_general,
        test_already_quoted,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed (total: {len(tests)})")
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed!")
