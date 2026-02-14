from core.state import StateManager
from core.planner import Planner

def test_planner():
    print("Testing Planner...")
    state = StateManager()
    planner = Planner(state)
    
    task = "Search google for 'Elon Musk' and save the results to elon.txt"
    print(f"Task: {task}")
    
    # Mocking LLM response or relying on real one if key exists
    # For this test, we hope the real LLM works or we handle the error gracefully
    try:
        plan = planner.create_plan(task)
        print("Generated Plan:")
        print(plan)
        
        if isinstance(plan, list):
            print("✅ Plan is a list.")
        else:
            print("❌ Plan format invalid.")
            
    except Exception as e:
        print(f"❌ Planning Error: {e}")

if __name__ == "__main__":
    test_planner()
