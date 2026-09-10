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


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not set. Add it to your environment / .env file."
            )
        _client = Groq(api_key=api_key)
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