import json
from core.llm_client import LLMClient

class Planner:
    def __init__(self, state):
        self.state = state
        self.llm = LLMClient()

    def create_plan(self, task):
        self.state.set("PLANNING")
        
        prompt = f"""
        You are a task planner for an AI Assistant.
        The user wants: "{task}"
        
        Available Tools:
        - browser.open_url(url)
        - browser.search_google(query)
        - files.read_file(path)
        - files.write_file(path, content)
        - system.execute_command(cmd)
        
        Return a JSON list of steps to complete this task. 
        Format:
        [
            {{"action": "browser.search_google", "args": ["query"]}},
            {{"action": "files.write_file", "args": ["path", "content"]}}
        ]
        
        Do not include markdown formatting. Just the JSON string.
        """
        
        response = self.llm.generate(prompt)
        
        try:
            # Clean response if LLM adds backticks
            response = response.strip().replace("```json", "").replace("```", "")
            steps = json.loads(response)
            return steps
        except Exception as e:
            print(f"❌ Planning Error: {e}")
            return []
