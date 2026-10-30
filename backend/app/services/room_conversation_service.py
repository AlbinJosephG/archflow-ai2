
import uuid

from app.schemas.room import RoomRequirements
from app.schemas.question import QuestionResponse

from app.services.room_requirement_extractor import (
    extract_room_requirements,
)
from app.services.room_question_engine import (
    generate_next_room_question,
)
from app.services.room_confirmation_service import (
    create_room_session,
    add_room_recommendations,
)
from app.services.room_recommendation_engine import (
    get_room_recommendations,
)
from app.services.session_store import (
    create_session,
    update_session,
)


def start_room_conversation(
    description: str,
) -> tuple:

    cleaned_description = description.strip()

    if not cleaned_description:
        raise ValueError("Room description cannot be empty.")

    # Step 1: Extract requirements from the description.
    requirements: RoomRequirements = extract_room_requirements(
        cleaned_description
    )

    if not isinstance(requirements, RoomRequirements):
        raise TypeError(
            "Room extractor must return RoomRequirements."
        )

    # Step 2: Create a new room session.
    session_id = str(uuid.uuid4())

    session = create_room_session(
        session_id=session_id,
        requirements=requirements,
    )

    # Step 3: Generate the next question.
    question_response = generate_next_room_question(
        session.requirements
    )

    if question_response.question is not None:

        # A core requirement is missing.
        session.active_question = question_response.question.field

        session.question_history.append(
            question_response.question.field
        )

    else:

        # All four core requirements are available.
        session.active_question = None

        # Generate recommendations immediately.
        recommendations = get_room_recommendations(
            session.requirements
        )

        # Store the returned updated session.
        session = add_room_recommendations(
            session,
            recommendations,
        )

    # Step 4: Save the session.
    create_session(session)

    return session, question_response
