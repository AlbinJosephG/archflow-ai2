
from app.schemas.room import RoomRequirements

from app.services.room_question_engine import (
    generate_next_room_question,
)


requirements = RoomRequirements(
    room_type="living room",
    room_width=15,
    room_length=20,
    dimension_unit="feet",
    style="modern",
    furniture=["sofa", "television"],
)

response = generate_next_room_question(requirements)

print("\nNext Room Question:\n")

print(response.model_dump_json(indent=4))
