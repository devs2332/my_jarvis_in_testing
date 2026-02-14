#!/usr/bin/env python3
"""
Comprehensive component test for Jarvis AI.
Tests all major components without requiring live microphone/speaker.
"""

import sys
import traceback
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_imports():
    """Test all critical imports."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing Imports{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    tests = [
        ("config", "import config"),
        ("core.agent", "from core.agent import Agent"),
        ("core.brain", "from core.brain import Brain"),
        ("core.memory", "from core.memory import Memory"),
        ("core.llm_client", "from core.llm_client import LLMClient"),
        ("core.state", "from core.state import StateManager"),
        ("core.intent_router", "from core.intent_router import IntentRouter"),
        ("core.planner", "from core.planner import Planner"),
        ("core.tools", "from core.tools import ToolRegistry"),
        ("tools.system", "from tools import system"),
        ("tools.browser", "from tools import browser"),
        ("tools.files", "from tools import files"),
        ("vision.screen_reader", "from vision.screen_reader import ScreenReader"),
        ("vision.image_analysis", "from vision.image_analysis import ImageAnalyzer"),
        ("vision.camera_analysis", "from vision.camera_analysis import CameraAnalyzer"),
    ]
    
    results = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  {GREEN}✓{RESET} {name}")
            results.append((name, True, None))
        except Exception as e:
            print(f"  {RED}✗{RESET} {name}: {str(e)}")
            results.append((name, False, str(e)))
    
    return results

def test_config():
    """Test configuration loading."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing Configuration{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = []
    
    try:
        import config
        print(f"  {GREEN}✓{RESET} Config file loaded")
        print(f"    LLM Provider: {config.LLM_PROVIDER}")
        
        # Check .env file
        env_file = Path(".env")
        if env_file.exists():
            print(f"  {GREEN}✓{RESET} .env file exists")
            results.append(("config_file", True, None))
        else:
            print(f"  {YELLOW}⚠{RESET} .env file not found (using defaults)")
            results.append(("env_file", False, ".env not found"))
            
    except Exception as e:
        print(f"  {RED}✗{RESET} Config error: {e}")
        results.append(("config", False, str(e)))
    
    return results

def test_json_files():
    """Test JSON data files."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing JSON Data Files{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    import json
    results = []
    
    json_files = [
        "data/user_profile.json",
        "data/memory.json"
    ]
    
    for filepath in json_files:
        path = Path(filepath)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                print(f"  {GREEN}✓{RESET} {filepath} - Valid JSON")
                results.append((filepath, True, None))
            except json.JSONDecodeError as e:
                print(f"  {RED}✗{RESET} {filepath} - Invalid JSON: {e}")
                results.append((filepath, False, str(e)))
        else:
            print(f"  {YELLOW}⚠{RESET} {filepath} - File not found")
            results.append((filepath, False, "File not found"))
    
    return results

def test_llm_client():
    """Test LLM client initialization."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing LLM Client{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = []
    
    try:
        from core.llm_client import LLMClient
        import config
        
        client = LLMClient()
        print(f"  {GREEN}✓{RESET} LLM Client initialized")
        print(f"    Provider: {config.LLM_PROVIDER}")
        
        # Try a simple query
        try:
            response = client.query("Say 'Hello' and nothing else")
            print(f"  {GREEN}✓{RESET} LLM Query successful")
            print(f"    Response: {response[:50]}...")
            results.append(("llm_query", True, None))
        except Exception as e:
            print(f"  {YELLOW}⚠{RESET} LLM Query failed: {e}")
            print(f"    (This may be due to missing API key)")
            results.append(("llm_query", False, str(e)))
            
    except Exception as e:
        print(f"  {RED}✗{RESET} LLM Client error: {e}")
        results.append(("llm_client", False, str(e)))
    
    return results

def test_agent():
    """Test Agent initialization."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing Agent{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = []
    
    try:
        from core.agent import Agent
        
        agent = Agent()
        print(f"  {GREEN}✓{RESET} Agent initialized")
        print(f"    State: {agent.state.current_state}")
        
        # Test simple query (skip if LLM not configured)
        try:
            response = agent.run("What is 2+2?")
            print(f"  {GREEN}✓{RESET} Agent query successful")
            print(f"    Response: {response[:100]}...")
            results.append(("agent_query", True, None))
        except Exception as e:
            print(f"  {YELLOW}⚠{RESET} Agent query failed: {e}")
            results.append(("agent_query", False, str(e)))
            
    except Exception as e:
        print(f"  {RED}✗{RESET} Agent error: {e}")
        results.append(("agent", False, str(e)))
    
    return results

def test_tools():
    """Test tool registry."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing Tools{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = []
    
    try:
        from core.tools import ToolRegistry
        
        registry = ToolRegistry()
        print(f"  {GREEN}✓{RESET} Tool Registry initialized")
        
        available_tools = registry.list_tools()
        print(f"  {GREEN}✓{RESET} Available tools: {len(available_tools)}")
        for tool in available_tools:
            print(f"    - {tool}")
        
        results.append(("tool_registry", True, None))
        
    except Exception as e:
        print(f"  {RED}✗{RESET} Tool Registry error: {e}")
        results.append(("tool_registry", False, str(e)))
    
    return results

def test_memory():
    """Test memory system."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing Memory System{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = []
    
    try:
        from core.memory import Memory
        
        memory = Memory()
        print(f"  {GREEN}✓{RESET} Memory initialized")
        
        # Test save/load
        test_data = {"test": "data", "timestamp": "2026-02-06"}
        memory.add_entry("test_user", "test_response", {"key": "value"})
        print(f"  {GREEN}✓{RESET} Memory entry added")
        
        results.append(("memory", True, None))
        
    except Exception as e:
        print(f"  {RED}✗{RESET} Memory error: {e}")
        results.append(("memory", False, str(e)))
    
    return results

def print_summary(all_results):
    """Print test summary."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    total = sum(len(results) for results in all_results)
    passed = sum(1 for results in all_results for _, success, _ in results if success)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    
    if failed > 0:
        print(f"\n{RED}Failed Tests:{RESET}")
        for results in all_results:
            for name, success, error in results:
                if not success:
                    print(f"  {RED}✗{RESET} {name}")
                    if error:
                        print(f"      {error}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if failed == 0:
        print(f"{GREEN}🎉 All tests passed!{RESET}")
        return 0
    else:
        print(f"{YELLOW}⚠ Some tests failed. Check errors above.{RESET}")
        return 1

def main():
    """Run all tests."""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  JARVIS AI - Component Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    all_results = []
    
    try:
        # Run tests
        all_results.append(test_imports())
        all_results.append(test_config())
        all_results.append(test_json_files())
        all_results.append(test_llm_client())
        all_results.append(test_agent())
        all_results.append(test_tools())
        all_results.append(test_memory())
        
        # Print summary
        return print_summary(all_results)
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Tests interrupted by user.{RESET}")
        return 1
    except Exception as e:
        print(f"\n{RED}Critical error during testing:{RESET}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
