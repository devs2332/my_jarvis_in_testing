
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import Agent

class TestFastMode(unittest.TestCase):
    def setUp(self):
        self.agent = Agent()
        self.agent.llm = MagicMock()
        self.agent.llm.generate.return_value = "Concise answer."
        self.agent.brain.search = MagicMock()
        self.agent.brain.search.search.return_value = [{'href': 'http://example.com', 'title': 'Example', 'body': 'Content'}]

    def test_fast_mode_trigger(self):
        """Test that 'FastMode:' prefix triggers fast mode logic"""
        with patch.object(self.agent.brain, 'think_stream') as mock_think_stream:
            # We must exhaust the async generator for the call to be registered properly
            import asyncio
            async def run_test():
                async for _ in self.agent.run_stream("FastMode: test query"):
                    pass
            asyncio.run(run_test())
            
            # Verify prefix stripped and flag passed
            mock_think_stream.assert_called_with(
                "test query", research_mode=False, fast_mode=True, 
                search_mode="none", language="English", provider=None, model=None
            )

    def test_fast_mode_brain_logic(self):
        """Test that fast mode uses deep research logic when forced"""
        # We need to mock scraping since fast mode forces it
        with patch('tools.browser.scrape_url', return_value="Scraped Content") as mock_scrape:
            import asyncio
            async def run_test():
                # By passing "none" search doesn't trigger, but passing "legacy" hits the old max_results heuristic
                async for _ in self.agent.brain.think_stream("test query", fast_mode=True, search_mode="legacy"):
                    pass
            asyncio.run(run_test())
            
            # Verify search called with legacy fast mode settings (max_results=1 defaults in older heuristic)
            self.agent.brain.search.search.assert_called_with("test query", max_results=1)
            
            # Verify scraping was called (logic forces scraping for the single result)
            mock_scrape.assert_called()

if __name__ == '__main__':
    unittest.main()
