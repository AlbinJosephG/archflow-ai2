from typing import Dict, Optional

from app.schemas.session import ConversationSession


# One shared session dictionary for building and room conversations.
sessions: Dict[str, ConversationSession] = {}


def create_session(session: ConversationSession) -> None:
    sessions[session.session_id] = session


def get_session(session_id: str) -> Optional[ConversationSession]:
    return sessions.get(session_id)


def update_session(session: ConversationSession) -> None:
    sessions[session.session_id] = session


def delete_session(session_id: str) -> None:
    sessions.pop(session_id, None)


def get_all_sessions() -> list[ConversationSession]:
    return list(sessions.values())