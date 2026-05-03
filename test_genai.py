import os
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
headers = {"Authorization": f"Bearer {api_key}"}
payload = {
    "model": "gemini-2.5-flash",
    "messages": [{"role": "user", "content": "Hello!"}]
}

resp = httpx.post(url, headers=headers, json=payload)
print(resp.status_code)
print(resp.text)
