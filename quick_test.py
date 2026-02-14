"""Quick test of Jarvis AI core components."""
import sys

print("Testing Jarvis AI Components...")
print("="*50)

errors = []

# Test 1: JSON Files
print("\n1. Testing JSON Files...")
try:
    import json
    from pathlib import Path
    
    user_profile = Path("data/user_profile.json")
    memory_file = Path("data/memory.json")
    
    if user_profile.exists():
        json.load(open(user_profile))
        print("  ✓ user_profile.json valid")
    else:
        errors.append("data/user_profile.json not found")
    
    if memory_file.exists():
        json.load(open(memory_file))
        print("  ✓ memory.json valid")
    else:
        errors.append("data/memory.json not found")
        
except Exception as e:
    errors.append(f"JSON test failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 2: Config
print("\n2. Testing Config...")
try:
    import config
    print(f"  ✓ Config loaded (Provider: {config.LLM_PROVIDER})")
except Exception as e:
    errors.append(f"Config failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 3: Core imports (skip DDGS to avoid hang)
print("\n3. Testing Core Imports...")
try:
    from core.state import StateManager
    print("  ✓ StateManager")
    from core.memory import Memory
    print("  ✓ Memory")
    from core.llm_client import LLMClient
    print("  ✓ LLMClient")
except Exception as e:
    errors.append(f"Core imports failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 4: Agent
print("\n4. Testing Agent...")
try:
    from core.agent import Agent
    agent = Agent()
    print(f"  ✓ Agent initialized (State: {agent.state.current_state})")
except Exception as e:
    errors.append(f"Agent failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 5: Tools
print("\n5. Testing Tools...")
try:
    from core.tools import ToolRegistry
    tools = ToolRegistry()
    tool_list = tools.list_tools()
    print(f"  ✓ Tools loaded ({len(tool_list)} tools)")
    for tool in tool_list:
        print(f"    - {tool}")
except Exception as e:
    errors.append(f"Tools failed: {e}")
    print(f"  ✗ Error: {e}")

# Test 6: Vision
print("\n6. Testing Vision Modules...")
try:
    from vision.screen_reader import ScreenReader
    print("  ✓ ScreenReader")
    from vision.image_analysis import ImageAnalyzer
    print("  ✓ ImageAnalyzer")
except Exception as e:
    errors.append(f"Vision imports failed: {e}")
    print(f"  ✗ Error: {e}")

# Summary
print("\n" + "="*50)
if errors:
    print(f"❌ {len(errors)} errors found:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("✅ All tests passed!")
    sys.exit(0)
