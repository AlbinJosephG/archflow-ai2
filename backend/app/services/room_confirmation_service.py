from app.schemas.room import RoomRequirements
from app.schemas.room_answer import ParsedRoomAnswer
from app.schemas.session import ConversationSession

from app.schemas.room_recommendation import (
    RoomRecommendation,
    RoomReadiness,
)

from app.services.room_requirement_updater import (
    update_room_requirements,
)


# Four essential fields for the initial room brief.
CORE_REQUIRED_FIELDS = {
    "room_type",
    "room_width",
    "room_length",
    "room_height",
}


# Physical information that must be confirmed before
# generating the final architectural scene.
SCENE_REQUIRED_FIELDS = {
    "room_type",
    "room_width",
    "room_length",
    "room_height",
    "dimension_unit",
    "door_count",
    "window_count",
}


# Fields for which AI recommendations are allowed.
RECOMMENDABLE_FIELDS = {
    "style",
    "wall_material",
    "wall_color",
    "flooring_material",
    "ceiling_type",
    "door_count",
    "window_count",
    "furniture",
    "lighting_preference",
}


def _validate_room_session(
    session: ConversationSession,
) -> None:
    """
    Ensure that this service only receives a room session.
    """

    if session.session_type != "room":
        raise ValueError(
            "Room confirmation operations require a room session."
        )

    if not isinstance(session.requirements, RoomRequirements):
        raise TypeError(
            "Room session must contain RoomRequirements."
        )


def has_value(value):
    """Check whether a requirement contains a meaningful value."""

    return value is not None and value != "" and value != []


def create_room_session(
    session_id: str,
    requirements: RoomRequirements | None = None,
) -> ConversationSession:
    """
    Create a room conversation using the unified session model.

    Existing non-empty requirements are treated as
    user-provided information.
    """

    requirements = requirements or RoomRequirements()

    field_sources = {}

    for field, value in requirements.model_dump().items():
        if has_value(value):
            field_sources[field] = "user_provided"

    return ConversationSession(
        session_id=session_id,
        session_type="room",
        requirements=requirements,
        question_history=[],
        recommendations={},
        field_sources=field_sources,
    )


def create_room_session_state(
    session_id: str,
    requirements: RoomRequirements | None = None,
) -> ConversationSession:
    """
    Backward-compatible factory name.

    Returns the unified ConversationSession, not a separate
    RoomSessionState object.
    """

    return create_room_session(session_id, requirements)


def record_user_answer(
    state: ConversationSession,
    parsed_answer: ParsedRoomAnswer,
) -> ConversationSession:
    """
    Store a user-provided answer as confirmed information.

    If the user provides a value for a field that previously
    had an AI recommendation, the recommendation is superseded.
    """

    _validate_room_session(state)

    field = parsed_answer.field

    updated_requirements = update_room_requirements(
        state.requirements,
        parsed_answer,
    )

    updated_sources = dict(state.field_sources)
    updated_sources[field] = "user_provided"

    # Track the unit as user-provided when explicitly supplied.
    if (
        field in {"room_width", "room_length", "room_height"}
        and parsed_answer.dimension_unit is not None
    ):
        updated_sources["dimension_unit"] = "user_provided"

    updated_recommendations = dict(state.recommendations)

    existing_recommendation = updated_recommendations.get(field)

    if (
        existing_recommendation
        and existing_recommendation.status == "pending"
    ):
        updated_recommendations[field] = (
            existing_recommendation.model_copy(
                update={"status": "superseded"}
            )
        )

    return state.model_copy(
        update={
            "requirements": updated_requirements,
            "field_sources": updated_sources,
            "recommendations": updated_recommendations,
        }
    )


def add_room_recommendations(
    state: ConversationSession,
    recommendations: dict,
) -> ConversationSession:
    """
    Store AI recommendations without applying them
    to actual room requirements.

    Expected input:
    {
        "style": {
            "value": "modern",
            "reason": "A clean interior style."
        }
    }
    """

    _validate_room_session(state)

    updated_recommendations = dict(state.recommendations)

    for field, recommendation in recommendations.items():

        if field not in RECOMMENDABLE_FIELDS:
            raise ValueError(
                f"AI recommendations are not allowed for: {field}"
            )

        # Never replace an existing user-provided value
        # or an already confirmed recommendation.
        existing_value = getattr(state.requirements, field)

        if has_value(existing_value):
            continue

        existing_recommendation = updated_recommendations.get(field)

        if (
            existing_recommendation
            and existing_recommendation.status
            in {"accepted", "rejected", "superseded"}
        ):
            continue

        value = recommendation.get("value")

        # Validate the suggested value against the
        # corresponding RoomRequirements field.
        RoomRequirements.model_validate({
            field: value
        })

        updated_recommendations[field] = RoomRecommendation(
            field=field,
            value=value,
            reason=recommendation.get("reason", ""),
            source="ai",
            status="pending",
        )

    return state.model_copy(
        update={
            "recommendations": updated_recommendations
        }
    )


def accept_room_recommendation(
    state: ConversationSession,
    field: str,
) -> ConversationSession:
    """
    Accept a pending recommendation and apply its value
    to actual room requirements.
    """

    _validate_room_session(state)

    recommendation = state.recommendations.get(field)

    if recommendation is None:
        raise ValueError(
            f"No recommendation exists for: {field}"
        )

    if recommendation.status != "pending":
        raise ValueError(
            f"Recommendation for {field} is not pending."
        )

    parsed_answer = ParsedRoomAnswer(
        field=field,
        value=recommendation.value,
    )

    updated_requirements = update_room_requirements(
        state.requirements,
        parsed_answer,
    )

    updated_sources = dict(state.field_sources)
    updated_sources[field] = "ai_recommendation_confirmed"

    updated_recommendations = dict(state.recommendations)

    updated_recommendations[field] = recommendation.model_copy(
        update={"status": "accepted"}
    )

    return state.model_copy(
        update={
            "requirements": updated_requirements,
            "field_sources": updated_sources,
            "recommendations": updated_recommendations,
        }
    )


def reject_room_recommendation(
    state: ConversationSession,
    field: str,
) -> ConversationSession:
    """
    Reject a pending recommendation without modifying
    the actual room requirements.
    """

    _validate_room_session(state)

    recommendation = state.recommendations.get(field)

    if recommendation is None:
        raise ValueError(
            f"No recommendation exists for: {field}"
        )

    if recommendation.status != "pending":
        raise ValueError(
            f"Recommendation for {field} is not pending."
        )

    updated_recommendations = dict(state.recommendations)

    updated_recommendations[field] = recommendation.model_copy(
        update={"status": "rejected"}
    )

    return state.model_copy(
        update={
            "recommendations": updated_recommendations
        }
    )


def get_room_readiness(
    state: ConversationSession,
) -> RoomReadiness:
    """
    Calculate initial brief completion and final
    architectural scene readiness.
    """

    _validate_room_session(state)

    requirements = state.requirements
    requirement_data = requirements.model_dump()

    # Check the four essential fields.
    missing_core_fields = [
        field
        for field in CORE_REQUIRED_FIELDS
        if not has_value(requirement_data.get(field))
    ]

    brief_completed = len(missing_core_fields) == 0

    # Check all physical information required for scene generation.
    missing_scene_fields = []
    unconfirmed_scene_fields = []

    for field in SCENE_REQUIRED_FIELDS:

        value = requirement_data.get(field)

        if not has_value(value):
            missing_scene_fields.append(field)
            continue

        if field not in state.field_sources:
            unconfirmed_scene_fields.append(field)

    scene_ready = (
        brief_completed
        and len(missing_scene_fields) == 0
        and len(unconfirmed_scene_fields) == 0
    )

    return RoomReadiness(
        brief_completed=brief_completed,
        scene_ready=scene_ready,
        missing_core_fields=sorted(missing_core_fields),
        missing_scene_fields=sorted(missing_scene_fields),
        unconfirmed_scene_fields=sorted(unconfirmed_scene_fields),
    )