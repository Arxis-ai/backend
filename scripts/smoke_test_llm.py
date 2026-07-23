import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.llm import generate_story_step


async def main():
    result = await generate_story_step(
        prompt="I choose to enter the left door",
        summary="Player is in a haunted castle.",
    )
    print("Generated JSON:", result)


if __name__ == "__main__":
    asyncio.run(main())
