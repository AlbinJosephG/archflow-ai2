from app.schemas.session import ConversationSession
from app.schemas.building import BuildingRequirements
from app.schemas.room import RoomRequirements

from app.services.session_store import (
    create_session,
    get_session,
    update_session,
    delete_session,
    get_all_sessions,
)

# --------------------------------
# TEST 1: Create a building session
# --------------------------------

building_session = ConversationSession(
    session_id="building-test-001",
    requirements=BuildingRequirements(
        building_type="house",
        bedrooms=3,
    ),
)

assert building_session.session_type == "building"
assert isinstance(building_session.requirements, BuildingRequirements)

print("TEST 1 PASSED: Building session created")


# --------------------------------
# TEST 2: Create a room session
# --------------------------------

room_session = ConversationSession(
    session_id="room-test-001",
    session_type="room",
    requirements={
        "room_type": "living room",
        "room_width": 15,
        "room_length": 20,
        "room_height": 10,
        "dimension_unit": "feet",
    },
)

assert room_session.session_type == "room"
assert isinstance(room_session.requirements, RoomRequirements)

print("TEST 2 PASSED: Room session created")


# --------------------------------
# TEST 3: Store both sessions
# --------------------------------

create_session(building_session)
create_session(room_session)

assert get_session("building-test-001") is not None
assert get_session("room-test-001") is not None

print("TEST 3 PASSED: Both sessions stored in one store")


# --------------------------------
# TEST 4: Update a session
# --------------------------------

room_session.question_history.append("style")
update_session(room_session)

stored_room = get_session("room-test-001")

assert stored_room.question_history == ["style"]

print("TEST 4 PASSED: Session updated")


# --------------------------------
# TEST 5: Retrieve all sessions
# --------------------------------

all_sessions = get_all_sessions()

assert len(all_sessions) == 2

print("TEST 5 PASSED: Both sessions retrieved")


# --------------------------------
# TEST 6: Delete a session
# --------------------------------

delete_session("room-test-001")

assert get_session("room-test-001") is None
assert get_session("building-test-001") is not None

print("TEST 6 PASSED: Session deleted correctly")


# --------------------------------
# TEST 7: Existing building imports
# --------------------------------

from app.services.conversation_service import start_conversation
from app.api.routes.building import router

print("TEST 7 PASSED: Existing building service and routes imported")


print("\nALL UNIFIED SESSION TESTS PASSED")