from app.schemas.room import RoomRequirements
from app.services.room_question_engine import generate_next_room_question


# Test 1: Height is missing.
room1 = RoomRequirements(
    room_type="living room",
    room_width=15,
    room_length=20,
    dimension_unit="feet",
    style="modern",
    furniture=["sofa"],
)

result1 = generate_next_room_question(room1)

print("TEST 1: Missing room height")
print(result1.model_dump())


# Test 2: All essential fields are present.
# Optional fields are intentionally missing.
room2 = RoomRequirements(
    room_type="living room",
    room_width=15,
    room_length=20,
    room_height=10,
    dimension_unit="feet",
)

result2 = generate_next_room_question(room2)

print("\nTEST 2: Core requirements completed")
print(result2.model_dump())