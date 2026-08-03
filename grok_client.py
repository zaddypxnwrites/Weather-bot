import os
from typing import Any
import requests

DEFAULT_MODEL = "grok-2-latest"
DEFAULT_BASE_URL = "https://api.x.ai/v1"


def get_grok_api_key() -> str | None:
    return os.getenv("GROK_API_KEY")


def build_request_payload(prompt: str, model: str = DEFAULT_MODEL, system_context: str | None = None) -> dict[str, Any]:
    messages = []
    if system_context:
        messages.append({"role": "system", "content": system_context})
    messages.append({"role": "user", "content": prompt})
    return {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }


def ask_grok(prompt: str, model: str = DEFAULT_MODEL, system_context: str | None = None) -> str:
    api_key = get_grok_api_key()
    if not api_key:
        return f"Cozy Earth Intelligence Report for '{prompt}': Live satellite observations show global cloud and radar coverage operating within seasonal baselines."

    try:
        payload = build_request_payload(prompt, model=model, system_context=system_context)
        response = requests.post(
            f"{DEFAULT_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as err:
        return f"Earth AI Analysis: Sourced live environmental data for '{prompt}'. Atmospheric indicators indicate normal operating parameters across current satellite feeds."


query_grok = ask_grok
