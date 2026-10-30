
from app.services.room_requirement_extractor import (
    extract_room_requirements
)


description = """
I want a modern living room.
The room should be 15 feet wide and 20 feet long.
I need a sofa, television and coffee table.
I prefer wooden flooring and warm lighting.
There should be two windows.
"""


requirements = extract_room_requirements(description)

print("\nExtracted Room Requirements:\n")

print(requirements.model_dump_json(indent=4))
