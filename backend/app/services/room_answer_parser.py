from app.schemas.room import RoomRequirements
from app.schemas.room_answer import ParsedRoomAnswer
from app.services.room_requirement_extractor import interpret_room_answer


ALLOWED_FIELDS = {
    "room_type",
    "room_width",
    "room_length",
    "room_height",
    "dimension_unit",
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

DIMENSION_FIELDS = {
    "room_width",
    "room_length",
    "room_height",
}

COUNT_FIELDS = {
    "door_count",
    "window_count",
}

TEXT_FIELDS = {
    "room_type",
    "style",
    "wall_material",
    "wall_color",
    "flooring_material",
    "ceiling_type",
    "lighting_preference",
    "special_requirements",
}

UNIT_MAPPING = {
    "feet": "feet",
    "foot": "feet",
    "ft": "feet",
    "meter": "meters",
    "meters": "meters",
    "metre": "meters",
    "metres": "meters",
    "m": "meters",
    "inch": "inches",
    "inches": "inches",
    "in": "inches",
}


class AnswerNeedsClarification(ValueError):
    def __init__(self, question: str):
        self.question = question
        super().__init__(question)


def validate_llm_answers(data: dict, requested_field: str):
    if data.get("needs_clarification"):
        question = data.get("clarification_question")
        raise AnswerNeedsClarification(
            question or "Could you please clarify your answer?"
        )

    answers = data.get("answers")

    if not isinstance(answers, list) or not answers:
        raise AnswerNeedsClarification(
            "I couldn't understand that answer. Could you rephrase it?"
        )

    parsed_answers = []
    seen_fields = set()

    # Find a common unit if the model returned one.
    common_unit = None

    for item in answers:
        if not isinstance(item, dict):
            raise AnswerNeedsClarification(
                "Could you please clarify your answer?"
            )

        field = item.get("field")
        value = item.get("value")

        if field not in ALLOWED_FIELDS:
            raise AnswerNeedsClarification(
                "I couldn't identify the room requirement. Could you rephrase it?"
            )

        if field in seen_fields:
            raise AnswerNeedsClarification(
                f"Could you clarify the value for {field.replace('_', ' ')}?"
            )

        seen_fields.add(field)

        if value is None:
            raise AnswerNeedsClarification(
                f"Could you clarify the value for {field.replace('_', ' ')}?"
            )

        if field in DIMENSION_FIELDS:
            unit = item.get("dimension_unit")

            if unit is not None:
                unit = UNIT_MAPPING.get(str(unit).lower().strip())

                if unit is None:
                    raise AnswerNeedsClarification(
                        "Should the room dimensions be in feet, metres, or inches?"
                    )

                if common_unit is not None and common_unit != unit:
                    raise AnswerNeedsClarification(
                        "You provided different units for the room dimensions. "
                        "Could you use the same unit for all dimensions?"
                    )

                common_unit = unit

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise AnswerNeedsClarification(
                    f"Please provide a numeric value for {field.replace('_', ' ')}."
                )

            if value <= 0:
                raise AnswerNeedsClarification(
                    f"{field.replace('_', ' ').capitalize()} must be greater than zero."
                )

        elif field in COUNT_FIELDS:
            if isinstance(value, bool) or not isinstance(value, int):
                raise AnswerNeedsClarification(
                    f"Please provide a whole number for {field.replace('_', ' ')}."
                )

            if value < 0:
                raise AnswerNeedsClarification(
                    f"{field.replace('_', ' ').capitalize()} cannot be negative."
                )

        elif field == "dimension_unit":
            normalized = UNIT_MAPPING.get(str(value).lower().strip())

            if normalized is None:
                raise AnswerNeedsClarification(
                    "Please specify feet, metres, or inches."
                )

            value = normalized

        elif field == "furniture":
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item.strip()
                for item in value
            ):
                raise AnswerNeedsClarification(
                    "Please clarify which furniture you want."
                )

        elif field in TEXT_FIELDS:
            if not isinstance(value, str) or not value.strip():
                raise AnswerNeedsClarification(
                    f"Please clarify {field.replace('_', ' ')}."
                )

        # Validate the field using the existing Pydantic schema.
        try:
            RoomRequirements.model_validate({field: value})
        except Exception as error:
            raise AnswerNeedsClarification(
                f"Please provide a valid value for {field.replace('_', ' ')}."
            ) from error

        parsed_answers.append(
            ParsedRoomAnswer(
                field=field,
                value=value,
                dimension_unit=(
                    common_unit
                    if field in DIMENSION_FIELDS
                    else None
                )
            )
        )

    if requested_field not in seen_fields:
        raise AnswerNeedsClarification(
            f"Could you please provide your {requested_field.replace('_', ' ')}?"
        )

    # Apply a common unit to every extracted dimension.
    if common_unit is not None:
        parsed_answers = [
            answer.model_copy(
                update={"dimension_unit": common_unit}
            )
            if answer.field in DIMENSION_FIELDS
            else answer
            for answer in parsed_answers
        ]

    return parsed_answers


def parse_room_answers(field: str, answer: str):
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Unsupported room field: {field}")

    answer = answer.strip()

    if not answer:
        raise AnswerNeedsClarification(
            "Please enter an answer."
        )

    data = interpret_room_answer(field, answer)

    return validate_llm_answers(data, field)


def parse_room_answer(field: str, answer: str) -> ParsedRoomAnswer:
    """
    Backward-compatible single-answer parser.
    Use parse_room_answers when multiple fields may be extracted.
    """
    parsed_answers = parse_room_answers(field, answer)

    if len(parsed_answers) != 1:
        raise AnswerNeedsClarification(
            "Your answer contains multiple room details. "
            "Please submit them through the room conversation."
        )

    return parsed_answers[0]