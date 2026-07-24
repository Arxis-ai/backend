import os
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.services.deepgram_auth import mint_scoped_key
from app.services.session_store import get_or_create_session
from app.services.supabase_client import parse_bearer_token, verify_jwt

router = APIRouter(prefix="/api/deepgram", tags=["deepgram"])


def _skip_auth() -> bool:
    return os.environ.get("DEV_SKIP_AUTH", "false").lower() == "true"


async def _current_user(authorization: str | None = Header(default=None)):
    if _skip_auth():
        return None

    return await verify_jwt(parse_bearer_token(authorization))


@router.post("/token")
async def create_deepgram_token(user=Depends(_current_user)):
    session_id = str(uuid4())
    get_or_create_session(
        session_id=session_id,
        user_id=getattr(user, "id", None) if user else None,
    )
    try:
        scoped_key = await mint_scoped_key(session_id=session_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not mint Deepgram scoped key",
        ) from exc

    return {
        "key": scoped_key["key"],
        "session_id": session_id,
        "expires_in": scoped_key["expires_in"],
    }
