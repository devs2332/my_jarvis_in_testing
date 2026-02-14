try:
    from ddgs import DDGS
    print("✅ Success: from ddgs import DDGS")
except ImportError:
    print("❌ Failed: from ddgs import DDGS")

try:
    import ddgs
    if hasattr(ddgs, 'DDGS'):
        print("✅ Success: ddgs.DDGS exists")
    else:
        print("❌ Failed: ddgs.DDGS does not exist")
        print(f"Dir: {dir(ddgs)}")
except ImportError:
    print("❌ Failed: import ddgs")
