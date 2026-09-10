from typing import Dict

from app.schemas.session import ConversationSession


sessions: Dict[str, ConversationSession] = {}


def create_session(session: ConversationSession):
    sessions[session.session_id] = session


def get_session(session_id: str):
    return sessions.get(session_id)


def update_session(session: ConversationSession):
    sessions[session.session_id] = session


def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]