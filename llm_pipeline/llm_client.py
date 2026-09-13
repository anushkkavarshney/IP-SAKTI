"""
Shared LLM client wrapper for IP-SAKTI Module 3.
Centralizes API calls so classification.py and generator.py don't duplicate
Groq setup, retries, or JSON-parsing logic.
"""

import os
import json
from pathlib import Path
from groq import Groq

try:
    from dotenv import load_dotenv
    # Explicitly point at the repo root .env, regardless of the current
    # working directory the script was launched from.
    _ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=_ENV_PATH)
except ImportError:
    # python-dotenv not installed -- fall back to whatever is already
    # in the environment (e.g. set via `set GROQ_API_KEY=...` in the shell).
    pass

_client = None

# Bounded per-operation timeout: an explicit client-level timeout keeps a
# degraded/slow Groq connection from stalling (the SDK's own read default is
# already 60s, but with up to 2 built-in retries a bad network could otherwise
# multiply that into several minutes). The frontend aborts /analyze at 120s,
# so a ~60s per-LLM-operation budget fails clearly instead of hanging.
GROQ_TIMEOUT_S = 60.0


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not set. Add it to your environment / .env file."
            )
        _client = Groq(api_key=api_key, timeout=GROQ_TIMEOUT_S)
    return _client


def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    model: str = "openai/gpt-oss-120b",
    temperature: float = 0.2,
) -> dict:
    """
    Calls the LLM and enforces JSON-only output using Groq's JSON mode.
    Returns a parsed Python dict. Raises ValueError if parsing fails
    (caller should treat this as an abstention signal, not crash the pipeline).
    """
    client = get_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )

    raw_text = response.choices[0].message.content

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM did not return valid JSON. Raw output: {raw_text[:500]}"
        ) from e