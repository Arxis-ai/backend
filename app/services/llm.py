import json
from pathlib import Path

from app.core.llm_client import get_llm_client, get_llm_model

_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "agent_config.json"
_CONFIG = json.loads(_CONFIG_PATH.read_text())


async def generate_story_step(prompt: str, summary: str) -> dict:
    client = get_llm_client()
    response = await client.chat.completions.create(
        model=get_llm_model(),
        messages=[
            {"role": "system", "content": _CONFIG["system_prompt"]},
            {
                "role": "user",
                "content": f"Story summary so far: {summary}\n\nPlayer action: {prompt}",
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "story_step",
                "strict": True,
                "schema": _CONFIG["output_schema"],
            },
        },
    )
    return json.loads(response.choices[0].message.content)
