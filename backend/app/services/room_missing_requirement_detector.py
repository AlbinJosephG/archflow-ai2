
from app.schemas.room import RoomRequirements


CORE_REQUIRED_FIELDS = {
    "room_type",
    "room_width",
    "room_length",
    "room_height",
    "dimension_unit",
}


def detect_missing_room_requirements(
    requirements: RoomRequirements
):
    missing = []

    # High-priority requirements
    high_priority_fields = {
        "room_type": "What type of room do you want to design?",
        "room_width": "What is the width of the room?",
        "room_length": "What is the length of the room?",
        "room_height": "What is the height of the room?",
    }

    for field, question in high_priority_fields.items():
        value = getattr(requirements, field)

        if value is None or value == "":
            missing.append({
                "field": field,
                "priority": "high",
                "question": question,
                "reason": "Required to establish the room's basic geometry."
            })

    # Dimension unit must be confirmed whenever dimensions exist.
    dimensions_available = all([
        requirements.room_width is not None,
        requirements.room_length is not None,
        requirements.room_height is not None,
    ])

    if dimensions_available and not requirements.dimension_unit:
        missing.append({
            "field": "dimension_unit",
            "priority": "high",
            "question": "Are your room dimensions in feet or metres?",
            "reason": "Required to convert room dimensions into accurate 3D geometry."
        })

    # Medium-priority requirements
    medium_priority_fields = {
        "style": "What interior design style would you prefer?",
        "door_count": "How many doors should the room have?",
        "window_count": "How many windows should the room have?",
        "furniture": "What furniture should be included?",
    }

    for field, question in medium_priority_fields.items():
        value = getattr(requirements, field)

        if value is None or value == []:
            missing.append({
                "field": field,
                "priority": "medium",
                "question": question,
                "reason": "Helps establish the room's interior design and layout."
            })

    # Low-priority requirements
    low_priority_fields = {
        "wall_material": "What wall material would you prefer?",
        "wall_color": "What wall colour would you prefer?",
        "flooring_material": "What flooring material would you prefer?",
        "ceiling_type": "What type of ceiling would you prefer?",
        "lighting_preference": "What lighting would you prefer?",
    }

    for field, question in low_priority_fields.items():
        value = getattr(requirements, field)

        if value is None or value == "":
            missing.append({
                "field": field,
                "priority": "low",
                "question": question,
                "reason": "Helps refine the room's appearance."
            })

    return missing


def detect_missing_core_room_requirements(
    requirements: RoomRequirements
):
    missing_requirements = detect_missing_room_requirements(
        requirements
    )

    return [
        item
        for item in missing_requirements
        if item["field"] in CORE_REQUIRED_FIELDS
    ]
