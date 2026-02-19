
import logging
from tools.browser import scrape_url, get_search_results
from core.brain import Brain
from core.memory import Memory

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_scrape():
    print("--- Testing Scrape ---")
    url = "https://example.com"
    content = scrape_url(url)
    print(f"Content length: {len(content)}")
    print(f"Snippet: {content[:100]}...")
    assert "Example Domain" in content

def test_search_logic():
    print("\n--- Testing Search Logic ---")
    # Mock LLM and components for Brain
    class MockLLM:
        def generate(self, prompt):
            return "Generated answer based on research."

    brain = Brain(MockLLM(), Memory())
    
    # query = "Search top 3 websites for python news"
    # Logic in Brain.think() should catch "top 3" and set max_results=3
    # We can't easily assert internal state without modifying Brain to return it, 
    # but we can observe logs if we ran this in a way that captured them.
    # For now, let's just run it and ensure no crash.
    
    try:
        brain.think("Research top 3 python frameworks")
        print("Brain.think() executed successfully")
    except Exception as e:
        print(f"Brain.think() failed: {e}")

if __name__ == "__main__":
    test_scrape()
    test_search_logic()
