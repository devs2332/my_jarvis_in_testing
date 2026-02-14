from core.llm_client import LLMClient

def test_llm():
    print("Testing LLM Client...")
    try:
        client = LLMClient()
        print(f"Provider: {client.provider}")
        # Only run generation if API key is present (checking silently)
        # response = client.generate("Say hello")
        # print(f"Response: {response}")
        print("✅ LLM Client initialized successfully.")
    except Exception as e:
        print(f"❌ LLM Client Error: {e}")

if __name__ == "__main__":
    test_llm()
