import os

import httpx

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

_ELEVENLABS_STREAM_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
_OPENAI_SPEECH_URL = "https://api.openai.com/v1/audio/speech"


def _provider() -> str:
    return os.environ.get("TTS_PROVIDER", "elevenlabs").lower()


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def stream_tts(text: str):
    normalized_text = text.strip()
    if not normalized_text:
        return

    provider = _provider()
    if provider == "elevenlabs":
        async for chunk in _stream_elevenlabs(normalized_text):
            yield chunk
    elif provider == "openai":
        async for chunk in _stream_openai_tts(normalized_text):
            yield chunk
    elif provider == "mock":
        yield normalized_text.encode("utf-8")
    else:
        raise ValueError(f"Unsupported TTS_PROVIDER: {provider}")


async def _stream_elevenlabs(text: str):
    api_key = _required_env("ELEVENLABS_API_KEY")
    voice_id = _required_env("ELEVENLABS_VOICE_ID")
    model_id = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_flash_v2_5")
    output_format = os.environ.get("ELEVENLABS_OUTPUT_FORMAT", "mp3_22050_32")

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            _ELEVENLABS_STREAM_URL.format(voice_id=voice_id),
            params={"output_format": output_format},
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json={
                "text": text,
                "model_id": model_id,
            },
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                if chunk:
                    yield chunk


async def _stream_openai_tts(text: str):
    api_key = (
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("LLM_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
    )
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY or LLM_API_KEY for OpenAI TTS")

    model = os.environ.get("OPENAI_TTS_MODEL", "tts-1")
    voice = os.environ.get("OPENAI_TTS_VOICE", "alloy")
    response_format = os.environ.get("OPENAI_TTS_FORMAT", "mp3")

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            _OPENAI_SPEECH_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json={
                "model": model,
                "voice": voice,
                "input": text,
                "response_format": response_format,
            },
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                if chunk:
                    yield chunk
