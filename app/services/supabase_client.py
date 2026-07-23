import asyncio
import os

from fastapi import Header, HTTPException, status

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


def _get_first_required_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value

    joined_names = " or ".join(names)
    raise RuntimeError(f"Missing required environment variable: {joined_names}")


def get_supabase():
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError(
            "Missing Supabase SDK. Install backend dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc

    return create_client(
        _get_first_required_env("SUPABASE_URL"),
        _get_first_required_env("SUPABASE_SECRET_KEY", "SUPABASE_SERVICE_ROLE_KEY"),
    )


def parse_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization must be a Bearer token",
        )

    return token


async def verify_jwt(token: str):
    def _get_user():
        return get_supabase().auth.get_user(token)

    try:
        response = await asyncio.to_thread(_get_user)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Supabase token",
        ) from exc

    user = getattr(response, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Supabase token",
        )

    return user


async def require_current_user(authorization: str | None = Header(default=None)):
    return await verify_jwt(parse_bearer_token(authorization))


async def check_db_connection() -> dict:
    def _query():
        return (
            get_supabase()
            .table("test_records")
            .select("id")
            .limit(1)
            .execute()
        )

    response = await asyncio.to_thread(_query)
    return {
        "status": "ok",
        "rows_checked": len(response.data or []),
    }
