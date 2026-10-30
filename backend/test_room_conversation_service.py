from unittest.mock import patch

from app.schemas.room import RoomRequirements
from app.schemas.question import (
    AdaptiveQuestion,
    QuestionResponse,
)

from app.services.room_conversation_service import (
    start_room_conversation,
)

from app.services.session_store import (
    get_session,
    delete_session,
)


def test_start_room_conversation():

    mock_requirements = RoomRequirements(
        room_type="living room",
        room_width=15,
        room_length=20,
        dimension_unit="feet",
    )

    mock_question_response = QuestionResponse(
        question=AdaptiveQuestion(
            field="room_height",
            question="What is the height of your room?",
            priority="high",
            reason="Room height is required for scene generation.",
        ),
        completed=False,
    )

    with patch(
        "app.services.room_conversation_service.extract_room_requirements",
        return_value=mock_requirements,
    ), patch(
        "app.services.room_conversation_service.generate_next_room_question",
        return_value=mock_question_response,
    ):

        session, question_response = start_room_conversation(
            "Create a modern living room, 15 feet wide and 20 feet long."
        )

    # Verify session type.
    assert session.session_type == "room"

    # Verify extracted requirements.
    assert session.requirements.room_type == "living room"
    assert session.requirements.room_width == 15
    assert session.requirements.room_length == 20

    # Verify missing core requirement question.
    assert question_response.question.field == "room_height"

    # Verify question history.
    assert session.question_history == ["room_height"]

    # Verify shared session store.
    stored_session = get_session(session.session_id)

    assert stored_session is not None
    assert stored_session.session_type == "room"

    # Clean up test session.
    delete_session(session.session_id)

    print("TEST PASSED: Room conversation started successfully")


def test_empty_description():

    try:
        start_room_conversation("   ")
        assert False, "Expected ValueError for empty description"

    except ValueError as error:
        assert "cannot be empty" in str(error)

    print("TEST PASSED: Empty description rejected")


if __name__ == "__main__":

    test_start_room_conversation()
    test_empty_description()

    print("\nALL ROOM CONVERSATION TESTS PASSED")