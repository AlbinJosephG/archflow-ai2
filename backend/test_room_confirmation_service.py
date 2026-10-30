from pprint import pprint

from app.schemas.room import RoomRequirements
from app.schemas.room_answer import ParsedRoomAnswer

from app.services.room_confirmation_service import (
    create_room_session_state,
    record_user_answer,
    add_room_recommendations,
    accept_room_recommendation,
    reject_room_recommendation,
    get_room_readiness,
)


# --------------------------------------------------
# TEST 1: Create a room session
# --------------------------------------------------

requirements = RoomRequirements(
    room_type="living room",
    room_width=15,
    room_length=20,
    room_height=10,
    dimension_unit="feet",
)

state = create_room_session_state(
    session_id="room-test-001",
    requirements=requirements,
)

print("\nTEST 1: Initial room session")

pprint(state.model_dump())

print("Readiness:")
pprint(get_room_readiness(state).model_dump())


# --------------------------------------------------
# TEST 2: Add AI recommendations
# --------------------------------------------------

recommendations = {
    "style": {
        "value": "modern",
        "reason": "A clean and practical interior style.",
    },
    "door_count": {
        "value": 1,
        "reason": "A single entry door is a starting suggestion.",
    },
    "window_count": {
        "value": 2,
        "reason": "Two windows are a starting suggestion.",
    },
    "wall_color": {
        "value": "warm white",
        "reason": "Creates a bright atmosphere.",
    },
}

state = add_room_recommendations(
    state,
    recommendations,
)

print("\nTEST 2: AI recommendations stored")

pprint(state.model_dump())

print("Readiness:")
pprint(get_room_readiness(state).model_dump())


# --------------------------------------------------
# TEST 3: Accept door recommendation
# --------------------------------------------------

state = accept_room_recommendation(
    state,
    "door_count",
)

print("\nTEST 3: Door recommendation accepted")

print("Door count:", state.requirements.door_count)

print("Source:", state.field_sources["door_count"])

print(
    "Recommendation status:",
    state.recommendations["door_count"].status,
)


# --------------------------------------------------
# TEST 4: Reject window recommendation
# --------------------------------------------------

state = reject_room_recommendation(
    state,
    "window_count",
)

print("\nTEST 4: Window recommendation rejected")

print("Window count:", state.requirements.window_count)

print(
    "Recommendation status:",
    state.recommendations["window_count"].status,
)


# --------------------------------------------------
# TEST 5: User provides actual window count
# --------------------------------------------------

state = record_user_answer(
    state,
    ParsedRoomAnswer(
        field="window_count",
        value=3,
    ),
)

print("\nTEST 5: User provides window count")

print("Window count:", state.requirements.window_count)

print("Source:", state.field_sources["window_count"])


# --------------------------------------------------
# TEST 6: Final readiness
# --------------------------------------------------

readiness = get_room_readiness(state)

print("\nTEST 6: Final room readiness")

pprint(readiness.model_dump())