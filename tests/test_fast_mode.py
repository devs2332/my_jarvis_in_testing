
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
        with patch.object(self.agent.brain, 'think') as mock_think:
            self.agent.run("FastMode: test query")
            
            # Verify prefix stripped and flag passed
            mock_think.assert_called_with("test query", research_mode=False, fast_mode=True)

    def test_fast_mode_brain_logic(self):
        """Test that fast mode limits results and forces scraping in Brain"""
        # We need to mock scraping since fast mode forces it
        with patch('tools.browser.scrape_url', return_value="Scraped Content") as mock_scrape:
            self.agent.brain.think("test query", fast_mode=True)
            
            # Verify search called with max_results=1
            self.agent.brain.search.search.assert_called_with("test query", max_results=1)
            
            # Verify scraping was called (logic forces scraping for the single result)
            mock_scrape.assert_called()

if __name__ == '__main__':
    unittest.main()
