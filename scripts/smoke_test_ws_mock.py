import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DEV_SKIP_AUTH"] = "true"
os.environ["TTS_PROVIDER"] = "mock"

from fastapi.testclient import TestClient

from app.main import app
from app.services import llm_stream_adapter


async def mock_stream_story_step(prompt: str, summary: str):
    yield "The hidden door opens."
    yield "A silver corridor hums."
    yield "Three paths wait ahead."
    yield {
        "story_id": "mock-story",
        "chapter_number": 1,
        "narrative_text": "The hidden door opens. A silver corridor hums. Three paths wait ahead.",
        "character_emotion": "curious",
        "choices": ["Step forward", "Call out", "Turn back"],
        "audio_prompt": "Read with quiet suspense.",
    }


def main():
    llm_stream_adapter.stream_story_step = mock_stream_story_step
    client = TestClient(app)

    with client.websocket_connect("/ws/story/mock-session") as websocket:
        websocket.send_json(
            {
                "type": "user_utterance",
                "text": "I open the hidden door.",
                "story_context": {"summary": "A mystery has begun.", "chapter_number": 1},
            }
        )

        messages = []
        while True:
            message = websocket.receive_json()
            messages.append(message)
            if message["type"] == "story_state":
                break

    print(
        {
            "ws_ok": True,
            "message_types": [message["type"] for message in messages],
            "audio_chunks": sum(1 for message in messages if message["type"] == "audio_chunk"),
        }
    )


if __name__ == "__main__":
    main()
