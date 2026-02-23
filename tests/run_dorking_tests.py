"""Quick validation script for QueryDorker — ASCII-only output."""
import sys, os, logging
logging.disable(logging.CRITICAL)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.google_dorking import QueryDorker

d = QueryDorker()
ok = 0
fail = 0
errors = []

# --- Intent detection ---
intent_tests = [
    ("python import error module not found", "coding"),
    ("latest AI news today 2026", "news"),
    ("research paper on neural networks arxiv", "academic"),
    ("how to setup django step by step beginner guide", "tutorial"),
    ("React vs Vue which is better", "comparison"),
    ("is tailwindcss worth it reddit review", "opinion"),
    ("CVE-2024-1234 vulnerability exploit", "security"),
    ("capital of France", "general"),
]
for q, exp in intent_tests:
    got = d._detect_intent(q)
    if got == exp:
        ok += 1
    else:
        fail += 1
        errors.append(f"INTENT: expected={exp} got={got} q={q}")

# --- Web search (single query) ---
ws = d.dork("python traceback import error", mode="web_search")
if len(ws) == 1 and "site:stackoverflow.com" in ws[0] and "-pinterest" in ws[0]:
    ok += 1
else:
    fail += 1
    errors.append(f"WS_CODING: {ws}")

ws = d.dork("research paper on transformers", mode="web_search")
if len(ws) == 1 and "filetype:pdf" in ws[0]:
    ok += 1
else:
    fail += 1
    errors.append(f"WS_ACADEMIC: {ws}")

ws = d.dork("latest tech news today", mode="web_search")
if len(ws) == 1 and "after:" in ws[0]:
    ok += 1
else:
    fail += 1
    errors.append(f"WS_NEWS: {ws}")

ws = d.dork("capital of France", mode="web_search")
if len(ws) == 1 and ws[0].strip():
    ok += 1
else:
    fail += 1
    errors.append(f"WS_GENERAL: {ws}")

ws = d.dork("", mode="web_search")
if ws == [""]:
    ok += 1
else:
    fail += 1
    errors.append(f"WS_EMPTY: {ws}")

# --- Deep research (multi-query) ---
dr = d.dork("python async await best practices", mode="deep_research")
if 2 <= len(dr) <= 3 and any("github.com" in q or "docs.python.org" in q for q in dr):
    ok += 1
else:
    fail += 1
    errors.append(f"DR_CODING: {dr}")

dr = d.dork("latest AI breakthroughs 2026", mode="deep_research")
if 2 <= len(dr) <= 3 and any("reuters.com" in q or "apnews.com" in q for q in dr):
    ok += 1
else:
    fail += 1
    errors.append(f"DR_NEWS: {dr}")

dr = d.dork("meaning of life", mode="deep_research")
if 2 <= len(dr) <= 3 and any("wikipedia.org" in q for q in dr):
    ok += 1
else:
    fail += 1
    errors.append(f"DR_GENERAL: {dr}")

# --- Already-quoted ---
ws = d.dork('"machine learning" site:arxiv.org', mode="web_search")
if len(ws) == 1 and '"machine learning"' in ws[0]:
    ok += 1
else:
    fail += 1
    errors.append(f"ALREADY_QUOTED: {ws}")

# --- Results ---
print(f"RESULTS: {ok} passed, {fail} failed")
if errors:
    for e in errors:
        print(f"  FAIL: {e}")
else:
    print("ALL TESTS PASSED")
