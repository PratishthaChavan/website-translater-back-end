import base64
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
def analyze_image(image_bytes, prompt, model="gemma3:12b", max_tokens=512):
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [encoded],
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": max_tokens,
            },
        },
        timeout=600,
    )
    if response.status_code != 200:
        print("BODY:", response.text)

    response.raise_for_status()
    data = response.json()

    return data["message"]["content"]