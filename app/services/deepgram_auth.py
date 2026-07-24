import os
from datetime import UTC, datetime, timedelta

import httpx

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

_DEEPGRAM_KEYS_URL = "https://api.deepgram.com/v1/projects/{project_id}/keys"
_DEFAULT_TTL_SECONDS = 300


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def mint_scoped_key(session_id: str) -> dict:
    api_key = _required_env("DEEPGRAM_API_KEY")
    project_id = _required_env("DEEPGRAM_PROJECT_ID")
    ttl_seconds = int(os.environ.get("DEEPGRAM_KEY_TTL_SECONDS", _DEFAULT_TTL_SECONDS))
    expiration_date = datetime.now(UTC) + timedelta(seconds=ttl_seconds)

    payload = {
        "comment": f"story-session-{session_id}",
        "scopes": ["usage:write"],
        "tags": ["story-session", session_id],
        "expiration_date": expiration_date.isoformat().replace("+00:00", "Z"),
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            _DEEPGRAM_KEYS_URL.format(project_id=project_id),
            headers={
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()

    data = response.json()
    key = data.get("key")
    if not key:
        raise RuntimeError("Deepgram key response did not include a key")

    return {
        "key": key,
        "expires_in": ttl_seconds,
    }
