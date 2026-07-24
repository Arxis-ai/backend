from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class StorySession:
    session_id: str
    user_id: str | None = None
    summary: str = ""
    chapter_number: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


_SESSIONS: dict[str, StorySession] = {}


def get_or_create_session(session_id: str, user_id: str | None = None) -> StorySession:
    session = _SESSIONS.get(session_id)
    if not session:
        session = StorySession(session_id=session_id, user_id=user_id)
        _SESSIONS[session_id] = session
    elif user_id and not session.user_id:
        session.user_id = user_id

    session.updated_at = datetime.now(UTC)
    return session


def update_session_context(
    session_id: str,
    summary: str | None = None,
    chapter_number: int | None = None,
) -> StorySession:
    session = get_or_create_session(session_id)
    if summary is not None:
        session.summary = summary
    if chapter_number is not None:
        session.chapter_number = chapter_number

    session.updated_at = datetime.now(UTC)
    return session
