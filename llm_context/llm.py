"""
llm.py — Send a context block to an LLM provider and return the response.

Supported providers
-------------------
- OpenAI  (gpt-4, gpt-4o, …)      → OPENAI_API_KEY
- Anthropic / Claude               → ANTHROPIC_API_KEY
- Google Gemini                    → GEMINI_API_KEY
- Ollama  (local)                  → no key needed
"""

from __future__ import annotations

import os
from typing import Optional


# ---------------------------------------------------------------------------
# Provider helpers
# ---------------------------------------------------------------------------


def _require_env(var: str) -> str:
    """
    Return the value of environment variable *var*.

    Raises
    ------
    EnvironmentError
        When the variable is not set or is empty.
    """
    value = os.environ.get(var, "").strip()
    if not value:
        raise EnvironmentError(
            f"Environment variable '{var}' is not set. Export it before running llm-context."
        )
    return value


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------


def _send_openai(context: str, model: str) -> str:
    """
    Send *context* to an OpenAI chat model and return the text response.

    Parameters
    ----------
    context:
        The assembled context block.
    model:
        OpenAI model identifier (e.g. ``"gpt-4o"``).

    Returns
    -------
    str
        The model's reply text.

    Raises
    ------
    EnvironmentError
        When ``OPENAI_API_KEY`` is missing.
    ImportError
        When the ``openai`` package is not installed.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "The 'openai' package is required to use OpenAI models. "
            "Install it with: pip install openai"
        ) from exc

    api_key = _require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": context}],
    )
    return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Anthropic / Claude
# ---------------------------------------------------------------------------


def _send_claude(context: str, model: str) -> str:
    """
    Send *context* to an Anthropic Claude model and return the text response.

    Parameters
    ----------
    context:
        The assembled context block.
    model:
        Anthropic model identifier (e.g. ``"claude-3-5-sonnet-20241022"``).
        If the caller passes the alias ``"claude"``, we default to the
        latest Sonnet model.

    Returns
    -------
    str
        The model's reply text.

    Raises
    ------
    EnvironmentError
        When ``ANTHROPIC_API_KEY`` is missing.
    ImportError
        When the ``anthropic`` package is not installed.
    """
    try:
        import anthropic
    except ImportError as exc:
        raise ImportError(
            "The 'anthropic' package is required to use Claude models. "
            "Install it with: pip install anthropic"
        ) from exc

    api_key = _require_env("ANTHROPIC_API_KEY")

    # Resolve the friendly alias to a real model name
    resolved_model = model
    if model.lower() == "claude":
        resolved_model = "claude-3-5-sonnet-20241022"

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=resolved_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": context}],
    )
    # content is a list of ContentBlock objects
    return "".join(block.text for block in message.content if hasattr(block, "text"))


# ---------------------------------------------------------------------------
# Google Gemini
# ---------------------------------------------------------------------------


def _send_gemini(context: str, model: str) -> str:
    """
    Send *context* to a Google Gemini model and return the text response.

    Parameters
    ----------
    context:
        The assembled context block.
    model:
        Gemini model identifier (e.g. ``"gemini-1.5-pro"``).
        If the caller passes the alias ``"gemini"``, defaults to
        ``"gemini-1.5-pro"``.

    Returns
    -------
    str
        The model's reply text.

    Raises
    ------
    EnvironmentError
        When ``GEMINI_API_KEY`` is missing.
    ImportError
        When the ``google-generativeai`` package is not installed.
    """
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise ImportError(
            "The 'google-generativeai' package is required to use Gemini models. "
            "Install it with: pip install google-generativeai"
        ) from exc

    api_key = _require_env("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    resolved_model = model
    if model.lower() == "gemini":
        resolved_model = "gemini-1.5-pro"

    gemini_model = genai.GenerativeModel(resolved_model)
    response = gemini_model.generate_content(context)
    return response.text or ""


# ---------------------------------------------------------------------------
# Ollama (local)
# ---------------------------------------------------------------------------


def _send_ollama(context: str, model: str, base_url: str = "http://localhost:11434") -> str:
    """
    Send *context* to a locally-running Ollama instance and return the
    text response.

    Parameters
    ----------
    context:
        The assembled context block.
    model:
        Ollama model tag (e.g. ``"llama3"``, ``"mistral"``).
        If the alias ``"ollama"`` is passed, defaults to ``"llama3"``.
    base_url:
        Base URL of the Ollama API server.

    Returns
    -------
    str
        The model's reply text.

    Raises
    ------
    ImportError
        When the ``requests`` package is not installed.
    ConnectionError
        When Ollama is not reachable.
    """
    try:
        import requests
    except ImportError as exc:
        raise ImportError(
            "The 'requests' package is required to use Ollama. "
            "Install it with: pip install requests"
        ) from exc

    resolved_model = model
    if model.lower() == "ollama":
        resolved_model = "llama3"

    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": resolved_model,
        "prompt": context,
        "stream": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError(
            f"Could not connect to Ollama at {base_url}. "
            "Make sure Ollama is running: 'ollama serve'"
        ) from exc

    data = resp.json()
    return data.get("response", "")


# ---------------------------------------------------------------------------
# Public dispatch
# ---------------------------------------------------------------------------

_PROVIDER_MAP: dict[str, str] = {
    "gpt-4o": "openai",
    "gpt-4": "openai",
    "claude": "claude",
    "gemini": "gemini",
    "ollama": "ollama",
}


def send(
    context: str,
    model: str = "gpt-4o",
    ollama_url: Optional[str] = None,
) -> str:
    """
    Send *context* to the appropriate LLM provider inferred from *model*.

    Parameters
    ----------
    context:
        The assembled context block string.
    model:
        One of ``"gpt-4o"``, ``"gpt-4"``, ``"claude"``, ``"gemini"``,
        ``"ollama"``, or any provider-native model name.
    ollama_url:
        Override the Ollama base URL (default: ``http://localhost:11434``).

    Returns
    -------
    str
        The LLM's response text.

    Raises
    ------
    ValueError
        When *model* cannot be mapped to a known provider.
    EnvironmentError
        When a required API key environment variable is not set.
    """
    normalized = model.lower()
    provider = _PROVIDER_MAP.get(normalized)

    # Heuristic fallback for model names not in the map
    if provider is None:
        if normalized.startswith("gpt"):
            provider = "openai"
        elif normalized.startswith("claude"):
            provider = "claude"
        elif normalized.startswith("gemini"):
            provider = "gemini"
        else:
            raise ValueError(
                f"Unknown model '{model}'. Supported aliases: " + ", ".join(_PROVIDER_MAP)
            )

    if provider == "openai":
        return _send_openai(context, model)
    if provider == "claude":
        return _send_claude(context, model)
    if provider == "gemini":
        return _send_gemini(context, model)
    if provider == "ollama":
        return _send_ollama(context, model, base_url=ollama_url or "http://localhost:11434")

    raise ValueError(f"Unhandled provider: {provider}")  # pragma: no cover
