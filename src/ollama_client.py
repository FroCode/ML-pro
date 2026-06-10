"""Thin client for the local Ollama HTTP API."""
from __future__ import annotations

import httpx

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, TEMPERATURE


def is_available(model: str | None = None) -> bool:
    model = model or OLLAMA_MODEL
    try:
        resp = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        resp.raise_for_status()
        models = resp.json().get("models", [])
        names = {m["name"] for m in models}
        base = model.split(":")[0]
        return any(
            n == model or n.startswith(f"{base}:") or n.split(":")[0] == base
            for n in names
        )
    except (httpx.HTTPError, KeyError, OSError):
        return False


def generate(
    prompt: str,
    *,
    model: str | None = None,
    temperature: float = TEMPERATURE,
    max_tokens: int = 512,
) -> tuple[str, float]:
    """Return (response_text, latency_seconds)."""
    model = model or OLLAMA_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
        resp = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data.get("response", "").strip(), float(data.get("total_duration", 0)) / 1e9
