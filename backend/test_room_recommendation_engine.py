from app.schemas.room import RoomRequirements
from app.services.room_recommendation_engine import (
    get_room_recommendations
)


# Test 1: Living room with only essential details.
room1 = RoomRequirements(
    room_type="living room",
    room_width=15,
    room_length=20,
    room_height=10,
    dimension_unit="feet",
)

recommendations1 = get_room_recommendations(room1)

print("TEST 1: Living room recommendations")

for field, recommendation in recommendations1.items():
    print(f"{field}: {recommendation}")


# Test 2: Preserve existing user preferences.
room2 = RoomRequirements(
    room_type="bedroom",
    room_width=12,
    room_length=14,
    room_height=10,
    dimension_unit="feet",
    style="minimalist",
    wall_color="light blue",
    furniture=["bed", "wardrobe"],
)

recommendations2 = get_room_recommendations(room2)

print("\nTEST 2: Existing preferences")

for field, recommendation in recommendations2.items():
    print(f"{field}: {recommendation}")


# Test 3: Verify original requirements remain unchanged.
print("\nTEST 3: Original room requirements")

print(room2.model_dump())