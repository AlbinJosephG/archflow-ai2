import uuid

from app.schemas.building import BuildingRequirements
from app.schemas.session import ConversationSession
from app.services.requirement_extractor import extract_requirements
from app.services.question_engine import generate_next_question
from app.services.session_store import create_session, get_session


def start_conversation(description: str):

    requirements = extract_requirements(description)

    session_id = str(uuid.uuid4())

    session = ConversationSession(
        session_id=session_id,
        requirements=requirements,
        question_history=[],
    )

    create_session(session)

    question_response = generate_next_question(requirements)

    if question_response.question:
        session.question_history.append(
            question_response.question.field
        )

    return session, question_response