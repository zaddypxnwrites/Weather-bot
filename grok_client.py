import os
from typing import Any

import requests

DEFAULT_MODEL = "grok-2-latest"
DEFAULT_BASE_URL = "https://api.x.ai/v1"


def get_grok_api_key() -> str:
    api_key = os.getenv("GROK_API_KEY")
    if api_key:
        return api_key
    raise ValueError("GROK_API_KEY is missing. Set it in your environment or .env file.")


def build_request_payload(prompt: str, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
    }


def ask_grok(prompt: str, model: str = DEFAULT_MODEL) -> str:
    api_key = get_grok_api_key()
    payload = build_request_payload(prompt, model=model)

    response = requests.post(
        f"{DEFAULT_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
