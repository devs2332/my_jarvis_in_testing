try:
    from duckduckgo_search import DDGS
    print("Import 'from duckduckgo_search import DDGS' successful (Old way)")
except ImportError:
    print("Import 'from duckduckgo_search import DDGS' failed")

try:
    import ddgs
    print(f"Import 'import ddgs' successful. Dir: {dir(ddgs)}")
except ImportError:
    print("Import 'import ddgs' failed")
