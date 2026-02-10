import os
import json
import requests

# Peut être surchargé via variable d'environnement
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("CRBOT_MODEL", "llama3.2:3b")

def generate(prompt: str, temperature: float = 0.1, max_tokens: int | None = None) -> str:
    """
    Envoie un prompt au modèle local via Ollama et retourne le texte généré.
    """
    payload: dict = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if max_tokens is not None:
        payload["options"]["num_predict"] = max_tokens

    headers = {"Content-Type": "application/json"}
    resp = requests.post(OLLAMA_URL, data=json.dumps(payload), headers=headers, timeout=1800)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "")
