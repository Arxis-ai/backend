from collections.abc import AsyncIterator

from app.services import llm


async def stream_story_step(prompt: str, summary: str) -> AsyncIterator[str | dict]:
    native_stream = getattr(llm, "stream_story_step", None)
    if native_stream:
        async for item in native_stream(prompt, summary):
            yield item
        return

    final_story = await llm.generate_story_step(prompt=prompt, summary=summary)
    narrative_text = final_story.get("narrative_text", "")
    for chunk in _word_chunks(narrative_text):
        yield chunk
    yield final_story


def _word_chunks(text: str, words_per_chunk: int = 12):
    words = text.split()
    for index in range(0, len(words), words_per_chunk):
        yield " ".join(words[index : index + words_per_chunk])
