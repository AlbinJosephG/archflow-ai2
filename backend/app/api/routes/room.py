
from fastapi import APIRouter, HTTPException, status

from app.schemas.room import RoomRequirements
from app.schemas.room_api import (
    StartRoomRequest,
    SubmitRoomAnswerRequest,
)

from app.services.room_conversation_service import (
    start_room_conversation,
)

from app.services.room_answer_parser import (
    parse_room_answers,
    parse_room_answer,
    AnswerNeedsClarification,
)

from app.services.room_question_engine import (
    generate_next_room_question,
)
from app.services.room_recommendation_engine import (
    get_room_recommendations,
)
from app.services.room_confirmation_service import (
    record_user_answer,
    add_room_recommendations,
    accept_room_recommendation,
    reject_room_recommendation,
    get_room_readiness,
)
from app.services.session_store import (
    get_session,
    update_session,
)


router = APIRouter(
    prefix="/room",
    tags=["Room"],
)


# --------------------------------------------------
# HELPER 1: VALIDATE ROOM SESSION
# --------------------------------------------------

def get_valid_room_session(session_id: str):

    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    if session.session_type != "room":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This session is not a room session.",
        )

    if not isinstance(session.requirements, RoomRequirements):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid room requirements in session.",
        )

    return session


# --------------------------------------------------
# HELPER 2: SERIALIZE SESSION
# --------------------------------------------------

def serialize_session(session):

    return {
        "session_id": session.session_id,
        "session_type": session.session_type,
        "requirements": session.requirements.model_dump(),
        "active_question": session.active_question,
        "question_history": session.question_history,
        "recommendations": {
            field: recommendation.model_dump()
            for field, recommendation in session.recommendations.items()
        },
        "field_sources": session.field_sources,
    }


# --------------------------------------------------
# 1. START ROOM CONVERSATION
# --------------------------------------------------

@router.post("/session")
def start_room_session(request: StartRoomRequest):

    try:
        session, question_response = start_room_conversation(
            request.description
        )

        return {
            "session": serialize_session(session),
            "question": (
                question_response.question.model_dump()
                if question_response.question
                else None
            ),
            "completed": question_response.completed,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )


# --------------------------------------------------
# 2. GET ROOM SESSION
# --------------------------------------------------

@router.get("/session/{session_id}")
def get_room_session(session_id: str):

    session = get_valid_room_session(session_id)

    return serialize_session(session)


# --------------------------------------------------
# 3. SUBMIT ROOM ANSWER
# --------------------------------------------------

@router.post("/session/{session_id}/answer")
def submit_room_answer(
    session_id: str,
    request: SubmitRoomAnswerRequest,
):

    session = get_valid_room_session(session_id)

    if session.active_question is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is no active question to answer.",
        )

    field = session.active_question

    try:
        # Step 1: Interpret every user answer using Qwen.

        parsed_answers = parse_room_answers(
            field,
            request.answer,
        )

        # Step 2: Apply every explicitly extracted answer.
        for parsed_answer in parsed_answers:
            session = record_user_answer(
                session,
                parsed_answer,
            )

        # Step 3: Generate the next question.
        question_response = generate_next_room_question(
            session.requirements
        )

        next_question = question_response.question

        if next_question is not None:

            session.active_question = next_question.field

            session.question_history.append(
                next_question.field
            )

        else:

            session.active_question = None

            recommendations = get_room_recommendations(
                session.requirements
            )

            session = add_room_recommendations(
                session,
                recommendations,
            )

        # Step 4: Persist the updated session.
        update_session(session)

        # Step 5: Return the updated session.
        return {
            "session": serialize_session(session),
            "question": (
                next_question.model_dump()
                if next_question
                else None
            ),
            "completed": question_response.completed,
            "recommendations": {
                field: recommendation.model_dump()
                for field, recommendation in session.recommendations.items()
            },
            "readiness": get_room_readiness(
                session
            ).model_dump(),
        }

    except AnswerNeedsClarification as error:

        # Do not update or overwrite the existing session.
        # Keep the current question active.
        return {
            "session": serialize_session(session),
            "question": {
                "field": field,
                "question": error.question,
            },
            "clarification_required": True,
            "completed": False,
        }

    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )


# --------------------------------------------------
# 4. GET ROOM RECOMMENDATIONS
# --------------------------------------------------

@router.get("/session/{session_id}/recommendations")
def get_recommendations(session_id: str):

    session = get_valid_room_session(session_id)

    return {
        field: recommendation.model_dump()
        for field, recommendation in session.recommendations.items()
    }


# --------------------------------------------------
# 5. ACCEPT RECOMMENDATION
# --------------------------------------------------

@router.post(
    "/session/{session_id}/recommendations/{field}/accept"
)
def accept_recommendation(
    session_id: str,
    field: str,
):

    session = get_valid_room_session(session_id)

    try:
        # IMPORTANT: The service returns a NEW session.
        session = accept_room_recommendation(
            session,
            field,
        )

        # Save the updated session.
        update_session(session)

        return {
            "message": "Recommendation accepted.",
            "session": serialize_session(session),
            "readiness": get_room_readiness(
                session
            ).model_dump(),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# --------------------------------------------------
# 6. REJECT RECOMMENDATION
# --------------------------------------------------

@router.post(
    "/session/{session_id}/recommendations/{field}/reject"
)
def reject_recommendation(
    session_id: str,
    field: str,
):

    session = get_valid_room_session(session_id)

    try:
        # IMPORTANT: The service returns a NEW session.
        session = reject_room_recommendation(
            session,
            field,
        )

        # Save the updated session.
        update_session(session)

        return {
            "message": "Recommendation rejected.",
            "session": serialize_session(session),
            "readiness": get_room_readiness(
                session
            ).model_dump(),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# --------------------------------------------------
# 7. CHECK ROOM READINESS
# --------------------------------------------------

@router.get("/session/{session_id}/readiness")
def room_readiness(session_id: str):

    session = get_valid_room_session(session_id)

    readiness = get_room_readiness(session)

    return readiness.model_dump()


# --------------------------------------------------
# 7. SUBMIT CUSTOM RECOMMENDATION VALUE
# --------------------------------------------------

@router.post(
    "/session/{session_id}/recommendations/{field}/custom"
)
def submit_custom_recommendation(
    session_id: str,
    field: str,
    request: SubmitRoomAnswerRequest,
):

    session = get_valid_room_session(session_id)

    # Check whether this recommendation exists.
    recommendation = session.recommendations.get(field)

    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found.",
        )

    # Only pending recommendations can be replaced here.
    if recommendation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This recommendation is no longer pending.",
        )

    try:
        # Parse the user's custom value using the existing parser.
        parsed_answer = parse_room_answer(
            field,
            request.answer,
        )

        # Save the custom value as user-provided.
        session = record_user_answer(
            session,
            parsed_answer,
        )

        # Persist the updated session.
        update_session(session)

        return {
            "message": "Custom value saved successfully.",
            "session": serialize_session(session),
            "readiness": get_room_readiness(
                session
            ).model_dump(),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
