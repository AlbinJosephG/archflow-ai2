
from app.schemas.room import RoomRequirements

from app.services.room_missing_requirement_detector import (
    detect_missing_room_requirements
)


requirements = RoomRequirements(
    room_type="living room",
    room_width=15,
    room_length=20,
    dimension_unit="feet",
    style="modern",
    furniture=["sofa", "television"]
)


missing = detect_missing_room_requirements(requirements)

print("\nMissing Room Requirements:\n")

for item in missing:

    print(
        f"Field: {item['field']} | "
        f"Priority: {item['priority']} | "
        f"Question: {item['question']}"
    )
