from app.schemas.room import RoomRequirements
from app.schemas.room_answer import ParsedRoomAnswer


ALLOWED_FIELDS = {
    "room_type",
    "room_width",
    "room_length",
    "room_height",
    "dimension_unit",  # ADD THIS
    "style",
    "wall_material",
    "wall_color",
    "flooring_material",
    "ceiling_type",
    "door_count",
    "window_count",
    "furniture",
    "lighting_preference",
    "special_requirements",
}


def update_room_requirements(
    requirements: RoomRequirements,
    parsed_answer: ParsedRoomAnswer,
) -> RoomRequirements:

    field = parsed_answer.field

    # Prevent updates to unsupported fields.
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Unsupported room field: {field}")

    value = parsed_answer.value

    # Copy existing requirements so other answers remain unchanged.
    updated_data = requirements.model_dump()

    # Update only the answered field.
    updated_data[field] = value

    # Update the unit only when the user explicitly provides one.
    if field in ["room_width", "room_length", "room_height"]:
        if parsed_answer.dimension_unit is not None:
            updated_data["dimension_unit"] = parsed_answer.dimension_unit

    # Revalidate the complete requirements object.
    return RoomRequirements.model_validate(updated_data)