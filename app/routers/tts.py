from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.services.tts_provider import stream_tts

router = APIRouter(prefix="/api", tags=["tts"])


@router.get("/tts")
async def text_to_speech(text: str = Query(min_length=1)):
    return StreamingResponse(stream_tts(text), media_type="audio/mpeg")
