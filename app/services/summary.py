from app.core.llm_client import get_llm_client, get_llm_model

_SUMMARY_SYSTEM_PROMPT = (
    "You compress interactive story history into a rolling summary. "
    "Given the prior summary (if any) and new story events, produce an updated "
    "summary of no more than 150 words that preserves key plot points, character "
    "state, and unresolved threads."
)


async def summarize_context(history: list[str]) -> str:
    if not history:
        return ""

    client = get_llm_client()
    response = await client.chat.completions.create(
        model=get_llm_model(),
        messages=[
            {"role": "system", "content": _SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(history)},
        ],
    )
    return response.choices[0].message.content.strip()
