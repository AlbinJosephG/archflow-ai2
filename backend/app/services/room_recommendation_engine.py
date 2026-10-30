from app.schemas.room import RoomRequirements


def get_room_recommendations(
    requirements: RoomRequirements
) -> dict:

    room_type = (requirements.room_type or "").lower().strip()

    recommendations = {}

    # Default recommendations for different room types
    furniture_defaults = {
        "living room": [
            "sofa",
            "television",
            "coffee table",
            "side table"
        ],
        "bedroom": [
            "bed",
            "wardrobe",
            "bedside table"
        ],
        "kitchen": [
            "kitchen cabinets",
            "refrigerator",
            "cooking stove"
        ],
        "dining room": [
            "dining table",
            "dining chairs",
            "sideboard"
        ],
        "study room": [
            "study desk",
            "office chair",
            "bookshelf"
        ],
    }

    # General design recommendations
    defaults = {
        "style": {
            "value": "modern",
            "reason": "A clean and practical interior design style."
        },
        "wall_material": {
            "value": "painted plaster",
            "reason": "A simple and versatile wall finish."
        },
        "wall_color": {
            "value": "warm white",
            "reason": "Creates a bright and neutral atmosphere."
        },
        "flooring_material": {
            "value": "wooden flooring",
            "reason": "Provides a warm and comfortable appearance."
        },
        "ceiling_type": {
            "value": "simple false ceiling",
            "reason": "Provides a clean ceiling design."
        },
        "lighting_preference": {
            "value": "warm ambient lighting",
            "reason": "Creates a comfortable and welcoming atmosphere."
        },
        "door_count": {
            "value": 1,
            "reason": "A single entry door is a basic starting suggestion. Confirm against the actual room."
        },
        "window_count": {
            "value": 2,
            "reason": "Two windows are a starting suggestion for natural light. Confirm against the actual room."
        },
    }

    # Add recommendations only for missing fields.
    for field, recommendation in defaults.items():

        current_value = getattr(requirements, field)

        if current_value is None or current_value == "":
            recommendations[field] = recommendation

    # Furniture recommendations based on room type.
    if not requirements.furniture:

        suggested_furniture = furniture_defaults.get(
            room_type,
            ["suitable storage", "appropriate seating"]
        )

        recommendations["furniture"] = {
            "value": suggested_furniture,
            "reason": f"Suggested furniture for a {room_type or 'general'} room."
        }

    return recommendations