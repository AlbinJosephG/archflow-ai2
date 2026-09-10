from fastapi import APIRouter

from app.schemas.building import (
    BuildingRequest,
    BuildingRequirements,
)

from app.schemas.answer import (
    UserAnswer,
    ParseAnswerRequest,
    ParsedAnswer,
    RecommendationAcceptance,
)

from app.schemas.session import CreateSessionRequest

from app.services.requirement_extractor import (
    extract_requirements,
)

from app.services.missing_requirement_detector import (
    detect_missing_requirements,
)

from app.services.question_engine import (
    generate_next_question,
)

from app.services.answer_parser import (
    parse_user_answer,
)

from app.services.requirement_updater import (
    update_requirements,
)

from app.services.conversation_service import (
    start_conversation,
)

from app.services.session_store import (
    get_session,
    update_session,
)
from app.services.recommendation_engine import (
    get_recommendation,
)
from app.services.recommendation_engine import (
    get_recommendation,
    is_recommendation_request,
)
from app.schemas.answer import ParsedAnswer

router = APIRouter(
    prefix="/building",
    tags=["Building"],
)


# --------------------------------------------------
# PHASE 2: REQUIREMENT EXTRACTION
# --------------------------------------------------

@router.post("/analyze")
def analyze_building(request: BuildingRequest):

    requirements = extract_requirements(
        request.description
    )

    return {
        "message": "Requirements extracted successfully",
        "requirements": requirements,
    }


# --------------------------------------------------
# PHASE 3: MISSING REQUIREMENT DETECTION
# --------------------------------------------------

@router.post("/detect-missing")
def detect_missing(request: BuildingRequest):

    requirements = extract_requirements(
        request.description
    )

    missing = detect_missing_requirements(
        requirements
    )

    return {
        "message": "Missing requirements detected",
        "requirements": requirements,
        "missing_requirements": missing,
    }


# --------------------------------------------------
# PHASE 4: NEXT QUESTION GENERATION
# --------------------------------------------------

@router.post("/next-question")
def next_question(requirements: BuildingRequirements):

    return generate_next_question(
        requirements
    )


# --------------------------------------------------
# PHASE 4: ANSWER PARSING
# OLD TESTING ENDPOINT
# --------------------------------------------------

@router.post("/parse-answer")
def parse_answer(request: ParseAnswerRequest):

    return parse_user_answer(
        request.field,
        request.answer
    )


# --------------------------------------------------
# PHASE 4: REQUIREMENT UPDATING
# --------------------------------------------------

@router.post("/update-requirements")
def update_building_requirements(
    requirements: BuildingRequirements,
    parsed_answer: ParsedAnswer,
):

    updated = update_requirements(
        requirements,
        parsed_answer,
    )

    return {
        "message": "Requirements updated successfully",
        "requirements": updated,
    }


# --------------------------------------------------
# PHASE 4F: CREATE BUILDING CONVERSATION SESSION
# --------------------------------------------------

@router.post("/session")
def create_building_session(
    request: CreateSessionRequest
):

    session, question_response = start_conversation(
        request.description
    )

    return {
        "message": "Building conversation started",
        "session_id": session.session_id,
        "requirements": session.requirements,
        "question": question_response.question,
        "completed": question_response.completed,
    }


# --------------------------------------------------
# PHASE 4F.7: PROCESS SESSION ANSWER
# --------------------------------------------------
@router.post("/session/{session_id}/answer")
def answer_session(
    session_id: str,
    request: UserAnswer,
):
    session = get_session(session_id)

    if session is None:
        return {
            "message": "Session not found"
        }

    if not session.question_history:
        return {
            "message": "No active question for this session"
        }

    # Get the current question field
    current_field = session.question_history[-1]

    # Check whether the user wants a recommendation
    if is_recommendation_request(request.answer):

        recommendation = get_recommendation(
            current_field,
            session.requirements
        )

        if recommendation is None:

            return {
                "message": "Recommendation not available",
                "session_id": session.session_id,
                "field": current_field,
            }

        # Store recommendation in session
        session.pending_recommendation = recommendation

        update_session(session)

        return {
            "message": "Recommendation generated",
            "session_id": session.session_id,
            "recommendation": recommendation,
            "requirements": session.requirements,
            "completed": False,
        }

    # Normal answer processing
    parsed_answer = parse_user_answer(
        current_field,
        request.answer
    )

    updated_requirements = update_requirements(
        session.requirements,
        parsed_answer
    )

    session.requirements = updated_requirements

    # Generate the next question
    question_response = generate_next_question(
        updated_requirements
    )

    # Store the next question field
    if question_response.question:

        session.question_history.append(
            question_response.question.field
        )

    update_session(session)

    return {
        "message": "Answer processed successfully",
        "session_id": session.session_id,
        "parsed_answer": parsed_answer,
        "requirements": session.requirements,
        "question": question_response.question,
        "completed": question_response.completed,
    }

@router.post("/recommend")
def recommend(
    field: str,
    requirements: BuildingRequirements,
):

    recommendation = get_recommendation(
        field,
        requirements
    )

    if recommendation is None:

        return {
            "message": "No recommendation available",
            "recommendation": None,
        }

    return {
        "message": "Recommendation generated successfully",
        "recommendation": recommendation,
    }

@router.post("/session/{session_id}/accept-recommendation")
def accept_recommendation(
    session_id: str,
    request: RecommendationAcceptance,
):

    session = get_session(session_id)

    if session is None:

        return {
            "message": "Session not found"
        }

    # Check whether a recommendation exists
    if session.pending_recommendation is None:

        return {
            "message": "No pending recommendation found",
            "session_id": session.session_id,
        }

    # User rejected recommendation
    if not request.accept:

        session.pending_recommendation = None

        update_session(session)

        return {
            "message": "Recommendation rejected",
            "session_id": session.session_id,
            "requirements": session.requirements,
        }

    recommendation = session.pending_recommendation

    field = recommendation["field"]
    value = recommendation["recommended_value"]

    # Convert stored recommendation into ParsedAnswer
    parsed_answer = ParsedAnswer(
        field=field,
        value=value,
    )

    # Update requirements
    updated_requirements = update_requirements(
        session.requirements,
        parsed_answer,
    )

    session.requirements = updated_requirements

    # Clear pending recommendation
    session.pending_recommendation = None

    # Generate next question
    question_response = generate_next_question(
        updated_requirements
    )

    # Store next question
    if question_response.question:

        session.question_history.append(
            question_response.question.field
        )

    update_session(session)

    return {
        "message": "Recommendation accepted successfully",
        "session_id": session.session_id,
        "requirements": session.requirements,
        "question": question_response.question,
        "completed": question_response.completed,
    }