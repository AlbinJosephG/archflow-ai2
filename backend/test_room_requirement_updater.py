from app.schemas.room import RoomRequirements
from app.schemas.room_answer import ParsedRoomAnswer
from app.services.room_requirement_updater import update_room_requirements


# Initial room information
requirements = RoomRequirements(
    room_type="living room",
    room_width=15,
    room_length=20,
    dimension_unit="feet",
    style="modern",
    furniture=["sofa", "television"],
)

print("BEFORE UPDATE")
print(requirements.model_dump())


# Test 1: Update room height
parsed_answer = ParsedRoomAnswer(
    field="room_height",
    value=10,
    dimension_unit="feet",
)

requirements = update_room_requirements(
    requirements,
    parsed_answer,
)

print("\nAFTER HEIGHT UPDATE")
print(requirements.model_dump())


# Test 2: Update window count
parsed_answer = ParsedRoomAnswer(
    field="window_count",
    value=3,
)

requirements = update_room_requirements(
    requirements,
    parsed_answer,
)

print("\nAFTER WINDOW UPDATE")
print(requirements.model_dump())


# Test 3: Update furniture
parsed_answer = ParsedRoomAnswer(
    field="furniture",
    value=["sofa", "television", "coffee table"],
)

requirements = update_room_requirements(
    requirements,
    parsed_answer,
)

print("\nAFTER FURNITURE UPDATE")
print(requirements.model_dump())