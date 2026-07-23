import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def first_required_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value

    joined_names = " or ".join(names)
    raise RuntimeError(f"Missing required environment variable: {joined_names}")


def sign_in() -> str:
    supabase_url = required_env("SUPABASE_URL").rstrip("/")
    api_key = first_required_env("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_SECRET_KEY")
    email = required_env("SUPABASE_TEST_EMAIL")
    password = required_env("SUPABASE_TEST_PASSWORD")

    response = httpx.post(
        f"{supabase_url}/auth/v1/token?grant_type=password",
        headers={
            "apikey": api_key,
            "Content-Type": "application/json",
        },
        json={
            "email": email,
            "password": password,
        },
        timeout=20.0,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def call_backend(access_token: str):
    backend_url = required_env("DEPLOYED_BACKEND_URL").rstrip("/")
    response = httpx.get(
        f"{backend_url}/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20.0,
    )
    response.raise_for_status()
    return response.json()


def main():
    access_token = sign_in()
    user = call_backend(access_token)
    print({"auth_ok": True, "user": user})


if __name__ == "__main__":
    main()
