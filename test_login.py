import requests
import json

url = "http://localhost:8000/api/v1/auth/login"
payload = {"email": "admin@jarvis.com", "password": "Admin123!"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Success! Received Access Token:")
        print(f"{data['access_token'][:30]}...")
    else:
        print("Failed to login:")
        print(response.text)
except Exception as e:
    print(f"Connection error: {e}")
