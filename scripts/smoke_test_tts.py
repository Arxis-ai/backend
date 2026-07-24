import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.tts_provider import stream_tts


async def main():
    output_path = Path(os.environ.get("TTS_TEST_OUTPUT", "test.mp3"))
    text = os.environ.get("TTS_TEST_TEXT", "Testing audio stream from the backend.")

    total_bytes = 0
    with output_path.open("wb") as file:
        async for chunk in stream_tts(text):
            file.write(chunk)
            total_bytes += len(chunk)

    print({"tts_ok": total_bytes > 0, "output": str(output_path), "bytes": total_bytes})


if __name__ == "__main__":
    asyncio.run(main())
