import requests, json

OLLAMA_HOST = "http://localhost:11434"

def generate(model: str, prompt: str, options: dict | None = None) -> dict:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    print(f"[INFO] Sending request to Ollama: {url}")
    print(f"[INFO] Model: {model}")
    print(f"[INFO] Prompt length: {len(prompt)}")
    if options:
        print(f"[INFO] Using options: {options}")
        payload["options"] = options
    try:
        r = requests.post(url, json=payload, timeout=600)
        print(f"[INFO] Ollama response status: {r.status_code}")
        r.raise_for_status()
        resp_json = r.json()
        print(f"[INFO] Ollama response keys: {list(resp_json.keys())}")
        return resp_json  # {'model':..., 'response': 'text', 'done': true, ...}
    except Exception as e:
        print(f"[ERROR] Ollama request failed: {e}")
        raise
