import sys
import os
import unittest

# Add project root path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.reasoning import ReasoningEngine

class TestModePrompts(unittest.TestCase):
    def setUp(self):
        self.reasoning = ReasoningEngine()
        self.query = "What is Python?"
        self.search_results = [{"title": "Python.org", "body": "Python is a programming language"}]

    def test_normal_mode_prompt_is_concise(self):
        prompt = self.reasoning.build_prompt(
            self.query, self.search_results, search_mode="none"
        )
        self.assertIn("CONCISE, DIRECT, and HELPFUL", prompt)
        self.assertIn("fewest words possible", prompt)
        self.assertNotIn("DEEP RESEARCH", prompt)
        
        # Only the formatting rules part shouldn't contain source citation instructions
        formatting_rules = prompt.split("FORMATTING RULES")[1].lower()
        self.assertNotIn("cite sources", formatting_rules)

    def test_web_search_prompt_has_sources(self):
        prompt = self.reasoning.build_prompt(
            self.query, self.search_results, search_mode="web_search"
        )
        self.assertIn("WEB SEARCH MODE", prompt)
        self.assertIn("MODERATELY DETAILED", prompt)
        self.assertIn("cite sources inline", prompt.lower())
        self.assertNotIn("ACADEMIC-QUALITY", prompt)

    def test_deep_research_prompt_is_comprehensive(self):
        prompt = self.reasoning.build_prompt(
            self.query, self.search_results, search_mode="deep_research"
        )
        self.assertIn("DEEP RESEARCH MODE", prompt)
        self.assertIn("ACADEMIC-QUALITY", prompt)
        self.assertIn("comprehensive report", prompt.lower())
        self.assertIn("## Detailed Analysis", prompt)

if __name__ == '__main__':
    unittest.main()
