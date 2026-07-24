import base64
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.services import llm_stream_adapter
from app.services.session_store import get_or_create_session, update_session_context
from app.services.supabase_client import verify_jwt
from app.services.tts_provider import stream_tts

router = APIRouter(tags=["story"])


def _skip_auth() -> bool:
    return os.environ.get("DEV_SKIP_AUTH", "false").lower() == "true"


async def _authenticate_websocket(websocket: WebSocket):
    if _skip_auth():
        return None

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    try:
        return await verify_jwt(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None


@router.websocket("/ws/story/{session_id}")
async def story_socket(websocket: WebSocket, session_id: str):
    user = await _authenticate_websocket(websocket)
    if not _skip_auth() and user is None:
        return

    await websocket.accept()
    get_or_create_session(
        session_id=session_id,
        user_id=getattr(user, "id", None) if user else None,
    )

    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") != "user_utterance":
                await websocket.send_json(
                    {"type": "error", "message": "Unsupported message type"}
                )
                continue

            await _handle_user_utterance(websocket, session_id, message)
    except WebSocketDisconnect:
        return


async def _handle_user_utterance(websocket: WebSocket, session_id: str, message: dict):
    seq = 0
    try:
        text = str(message.get("text", "")).strip()
        story_context = message.get("story_context") or {}
        summary = str(story_context.get("summary", ""))
        chapter_number = story_context.get("chapter_number")
        update_session_context(
            session_id=session_id,
            summary=summary,
            chapter_number=chapter_number if isinstance(chapter_number, int) else None,
        )

        if not text:
            await websocket.send_json({"type": "error", "message": "Missing text"})
            return

        final_story = None
        async for item in llm_stream_adapter.stream_story_step(
            prompt=text,
            summary=summary,
        ):
            if isinstance(item, str):
                async for audio_chunk in stream_tts(item):
                    await websocket.send_json(
                        {
                            "type": "audio_chunk",
                            "data": base64.b64encode(audio_chunk).decode("ascii"),
                            "seq": seq,
                        }
                    )
                    seq += 1
            elif isinstance(item, dict):
                final_story = item

        await websocket.send_json({"type": "audio_end", "seq": max(seq - 1, 0)})
        if final_story:
            await websocket.send_json({"type": "story_state", **final_story})
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
