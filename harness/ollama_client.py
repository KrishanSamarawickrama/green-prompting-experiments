import requests, json

OLLAMA_HOST = "http://localhost:11434"

def generate(model: str, prompt: str, options: dict | None = None) -> dict:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    if options:
        payload["options"] = options
    r = requests.post(url, json=payload, timeout=600)
    r.raise_for_status()
    return r.json()  # {'model':..., 'response': 'text', 'done': true, ...}
