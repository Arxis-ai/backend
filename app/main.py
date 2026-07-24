from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.deepgram_token import router as deepgram_router
from app.routers.health import router as health_router
from app.routers.story_ws import router as story_ws_router
from app.routers.tts import router as tts_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(deepgram_router)
app.include_router(health_router)
app.include_router(story_ws_router)
app.include_router(tts_router)
