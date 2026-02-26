import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import Agent

class TestFeatureToggles(unittest.TestCase):
    def setUp(self):
        self.agent = Agent()
        # Mock LLM
        self.agent.llm = MagicMock()
        self.agent.llm.generate.return_value = "Mock response"
        self.agent.llm.generate_stream.return_value = ["Mock", " ", "response"]
        
        # Mock Search
        self.agent.brain.search = MagicMock()
        # Mock both single and multiple search methods
        self.agent.brain.search.search.return_value = [{'href': 'http://example.com', 'title': 'Example', 'body': 'Content'}]
        self.agent.brain.search.search_multiple.return_value = [{'href': 'http://example.com', 'title': 'Example', 'body': 'Content'}]

    def test_language_hindi_instruction(self):
        with patch.object(self.agent.brain.reasoning, 'build_prompt', return_value="Base Prompt") as mock_build_prompt:
            # We must exhaust the async generator for the call to be registered properly
            import asyncio
            async def run_test():
                async for _ in self.agent.run_stream("hindimode: Hello"):
                    pass
            asyncio.run(run_test())
            
            # Verify the language argument was passed to build_prompt
            called_kwargs = mock_build_prompt.call_args[1]
            self.assertEqual(called_kwargs.get("language"), "Hindi")

    def test_research_mode_triggers_scraping(self):
        with patch('tools.browser.scrape_url') as mock_scrape:
            mock_scrape.return_value = "Scraped Content"
            
            self.agent.run("tell me about cats", search_mode="deep_research")
            
            # Since deep_research uses dorking and search_multiple
            assert self.agent.brain.search.search_multiple.called
            mock_scrape.assert_called()

if __name__ == '__main__':
    unittest.main()
