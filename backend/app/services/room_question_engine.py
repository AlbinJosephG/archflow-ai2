
from app.schemas.room import RoomRequirements

from app.schemas.question import (
    AdaptiveQuestion,
    QuestionOption,
    QuestionResponse,
)

from app.services.room_missing_requirement_detector import (
    detect_missing_core_room_requirements
)


def generate_next_room_question(
    requirements: RoomRequirements,
) -> QuestionResponse:

    missing = detect_missing_core_room_requirements(requirements)

    if not missing:
        return QuestionResponse(
            question=None,
            completed=True,
        )

    # Priority order
    priority_order = {
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    missing.sort(
        key=lambda item: priority_order[item["priority"]]
    )

    next_requirement = missing[0]

    field = next_requirement["field"]
    priority = next_requirement["priority"]
    reason = next_requirement["reason"]

    # Room type
    if field == "room_type":

        question = AdaptiveQuestion(
            field="room_type",
            question="Which room would you like to design?",
            priority=priority,
            reason=reason,
            options=[
                QuestionOption(label="Living room", value="living room"),
                QuestionOption(label="Bedroom", value="bedroom"),
                QuestionOption(label="Kitchen", value="kitchen"),
                QuestionOption(label="Dining room", value="dining room"),
                QuestionOption(label="Home office", value="office"),
            ],
        )

    # Room dimensions
    elif field == "room_width":

        question = AdaptiveQuestion(
            field="room_width",
            question="What is the approximate width of the room?",
            priority=priority,
            reason=reason,
        )

    elif field == "room_length":

        question = AdaptiveQuestion(
            field="room_length",
            question="What is the approximate length of the room?",
            priority=priority,
            reason=reason,
        )

    elif field == "room_height":

        question = AdaptiveQuestion(
            field="room_height",
            question="What is the approximate height of the room?",
            priority=priority,
            reason=reason,
        )

    # Dimension unit
    elif field == "dimension_unit":

        question = AdaptiveQuestion(
            field="dimension_unit",
            question="Your room dimensions are provided. Are these measurements in feet or metres?",
            priority=priority,
            reason=reason,
            options=[
                QuestionOption(label="Feet (ft)", value="feet"),
                QuestionOption(label="Metres (m)", value="meters"),
            ],
        )

    # Openings
    elif field == "door_count":

        question = AdaptiveQuestion(
            field="door_count",
            question="How many doors should the room have?",
            priority=priority,
            reason=reason,
            options=[
                QuestionOption(label="No doors", value="0"),
                QuestionOption(label="1 door", value="1"),
                QuestionOption(label="2 doors", value="2"),
                QuestionOption(label="3 doors", value="3"),
            ],
        )

    elif field == "window_count":

        question = AdaptiveQuestion(
            field="window_count",
            question="How many windows should the room have?",
            priority=priority,
            reason=reason,
            options=[
                QuestionOption(label="No windows", value="0"),
                QuestionOption(label="1 window", value="1"),
                QuestionOption(label="2 windows", value="2"),
                QuestionOption(label="3 windows", value="3"),
                QuestionOption(label="4 windows", value="4"),
            ],
        )

    # Furniture
    elif field == "furniture":

        question = AdaptiveQuestion(
            field="furniture",
            question="What furniture would you like in this room?",
            priority=priority,
            reason=reason,
        )

    # Interior design preferences
    elif field == "style":

        question = AdaptiveQuestion(
            field="style",
            question="Which interior design style would you prefer?",
            priority=priority,
            reason=reason,
            options=[
                QuestionOption(label="Modern", value="modern"),
                QuestionOption(label="Minimalist", value="minimalist"),
                QuestionOption(label="Traditional", value="traditional"),
                QuestionOption(label="Contemporary", value="contemporary"),
                QuestionOption(label="Industrial", value="industrial"),
            ],
        )

    elif field == "wall_material":

        question = AdaptiveQuestion(
            field=field,
            question="What wall material would you prefer?",
            priority=priority,
            reason=reason,
        )

    elif field == "wall_color":

        question = AdaptiveQuestion(
            field=field,
            question="What wall colour would you prefer?",
            priority=priority,
            reason=reason,
        )

    elif field == "flooring_material":

        question = AdaptiveQuestion(
            field=field,
            question="What flooring material would you prefer?",
            priority=priority,
            reason=reason,
        )

    elif field == "ceiling_type":

        question = AdaptiveQuestion(
            field=field,
            question="What type of ceiling would you prefer?",
            priority=priority,
            reason=reason,
        )

    elif field == "lighting_preference":

        question = AdaptiveQuestion(
            field=field,
            question="What lighting would you prefer?",
            priority=priority,
            reason=reason,
            options=[
                QuestionOption(label="Warm lighting", value="warm lighting"),
                QuestionOption(label="Cool lighting", value="cool lighting"),
                QuestionOption(label="Natural lighting", value="natural lighting"),
                QuestionOption(label="LED lighting", value="LED lighting"),
            ],
        )

    else:

        question = AdaptiveQuestion(
            field=field,
            question=f"Please specify your {field}.",
            priority=priority,
            reason=reason,
        )

    return QuestionResponse(
        question=question,
        completed=False,
    )
