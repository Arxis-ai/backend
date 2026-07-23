import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

_DEFAULT_MODEL = "gpt-4o-mini"


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _first_env_with_name(*names: str) -> tuple[str, str] | tuple[None, None]:
    for name in names:
        value = os.environ.get(name)
        if value:
            return name, value
    return None, None


def get_llm_model() -> str:
    return _first_env("LLM_MODEL", "OPENAI_MODEL", "OPENROUTER_MODEL") or _DEFAULT_MODEL


def get_llm_client():
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Missing OpenAI SDK. Install backend dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc

    api_key_name, api_key = _first_env_with_name(
        "LLM_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"
    )
    if not api_key:
        raise RuntimeError(
            "Missing LLM API key. Set LLM_API_KEY for the configured endpoint, "
            "or set OPENAI_API_KEY / OPENROUTER_API_KEY."
        )

    base_url = _first_env("LLM_BASE_URL", "OPENAI_BASE_URL", "OPENROUTER_BASE_URL")
    if api_key_name == "OPENROUTER_API_KEY" and not base_url:
        raise RuntimeError(
            "OPENROUTER_API_KEY requires LLM_BASE_URL or OPENROUTER_BASE_URL in .env. "
            "Use LLM_BASE_URL=https://openrouter.ai/api/v1 for the OpenRouter proxy, "
            "or switch to LLM_API_KEY/OPENAI_API_KEY for native OpenAI."
        )

    client_kwargs = {"api_key": api_key, "timeout": 30.0}
    if base_url:
        client_kwargs["base_url"] = base_url

    return AsyncOpenAI(**client_kwargs)
