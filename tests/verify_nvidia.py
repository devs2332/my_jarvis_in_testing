
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_client import LLMClient
from config import LLM_PROVIDER

print(f"Current Provider Config: {LLM_PROVIDER}")

try:
    client = LLMClient()
    print("Client initialized.")
    
    prompt = "Hello! Who are you?"
    print(f"Sending prompt: {prompt}")
    
    response = client.generate(prompt)
    print(f"Response: {response}")
    
    print("-" * 20)
    print("Testing Stream...")
    for chunk in client.generate_stream(prompt):
        print(chunk, end="", flush=True)
    print("\nStream complete.")

except Exception as e:
    print(f"Error: {e}")
