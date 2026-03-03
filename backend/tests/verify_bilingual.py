import requests
import json
import time

API_URL = "http://127.0.0.1:8080/api/chat"

def test_chat(message, language=None):
    payload = {"message": message}
    if language:
        payload["language"] = language
    
    try:
        print(f"Sending: {message} (Language: {language})")
        res = requests.post(API_URL, json=payload, timeout=60)
        if res.status_code == 200:
            response = res.json().get("response", "")
            print(f"Response: {response[:100]}...")
            return response
        else:
            print(f"Error: {res.status_code} - {res.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def is_hindi(text):
    # Check for Devanagari range
    if not text: return False
    return any("\u0900" <= c <= "\u097F" for c in text)

print("--- Verifying Bilingual Mode ---")
time.sleep(5) # Wait for reload

# 1. Default (English)
r1 = test_chat("Who created Python?")
if r1:
    if not is_hindi(r1):
        print("PASS: Default is English")
    else:
        print("FAIL: Default contained Hindi")
else:
    print("FAIL: No response")

# 2. Hindi Mode via Prefix
r2 = test_chat("HindiMode: Who created Python?")
if r2:
    if is_hindi(r2):
        print("PASS: HindiMode prefix triggered Hindi")
    else:
        print("FAIL: HindiMode prefix did NOT trigger Hindi")
else:
    print("FAIL: No response")

# 3. Hindi Mode via API (Explicit)
r3 = test_chat("Who created Python?", language="Hindi")
if r3:
    if is_hindi(r3):
        print("PASS: API language='Hindi' triggered Hindi")
    else:
        print("FAIL: API language='Hindi' did NOT trigger Hindi")
else:
    print("FAIL: No response")
