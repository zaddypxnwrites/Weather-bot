import os

import pytest

from grok_client import build_request_payload, get_grok_api_key


def test_build_request_payload_uses_defaults(monkeypatch):
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    payload = build_request_payload("Hello")

    assert payload["model"] == "grok-2-latest"
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][0]["content"] == "Hello"


def test_get_grok_api_key_raises_when_missing(monkeypatch):
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GROK_API_KEY"):
        get_grok_api_key()
