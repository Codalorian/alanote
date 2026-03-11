import requests

API_KEY = "YOUR_XAI_API_KEY"

url = "https://api.x.ai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "grok-2-latest",
    "messages": [
        {"role": "user", "content": "Explain black holes in one sentence."}
    ]
}

response = requests.post(url, headers=headers, json=data)

print(response.json()["choices"][0]["message"]["content"])
