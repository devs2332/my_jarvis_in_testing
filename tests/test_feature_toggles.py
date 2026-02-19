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
        self.agent.brain.search.search.return_value = [{'href': 'http://example.com', 'title': 'Example', 'body': 'Content'}]

    def test_language_hindi_instruction(self):
        with patch.object(self.agent.brain.reasoning, 'build_prompt', return_value="Base Prompt"):
            self.agent.run("Hello", language="hi")
            
            call_args = self.agent.llm.generate.call_args
            prompt_used = call_args[0][0]
            self.assertIn("IMPORTANT: Please answer the above question in Hindi", prompt_used)

    def test_research_mode_triggers_scraping(self):
        with patch('tools.browser.scrape_url') as mock_scrape:
            mock_scrape.return_value = "Scraped Content"
            
            self.agent.run("tell me about cats", research_mode=True)
            
            self.agent.brain.search.search.assert_called_with("tell me about cats", max_results=10)
            mock_scrape.assert_called()

if __name__ == '__main__':
    unittest.main()
