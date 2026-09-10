from app.schemas.building import BuildingRequirements
from app.schemas.question import (
    AdaptiveQuestion,
    QuestionOption,
    QuestionResponse,
)
from app.services.missing_requirement_detector import (
    detect_missing_requirements,
)


def generate_next_question(
    requirements: BuildingRequirements,
) -> QuestionResponse:

    missing_response = detect_missing_requirements(requirements)

    missing = missing_response.missing_requirements

    if not missing:
        return QuestionResponse(
            question=None,
            completed=True,
        )

    # Select the highest-priority missing requirement
    priority_order = {
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    missing.sort(
        key=lambda item: priority_order[item.priority]
    )

    next_requirement = missing[0]

    field = next_requirement.field

    if field == "plot_dimensions":
        question = AdaptiveQuestion(
            field="plot_dimensions",
            question=(
                "What is the approximate size of your plot? "
                "For example, 40 × 60 feet."
            ),
            priority="high",
            reason=next_requirement.reason,
        )

    elif field == "floors":
        question = AdaptiveQuestion(
            field="floors",
            question="How many floors would you like?",
            priority="high",
            reason=next_requirement.reason,
            options=[
                QuestionOption(label="1 floor", value="1"),
                QuestionOption(label="2 floors", value="2"),
                QuestionOption(label="3 floors", value="3"),
            ],
        )

    elif field == "bedrooms":
        question = AdaptiveQuestion(
            field="bedrooms",
            question="How many bedrooms do you need?",
            priority="high",
            reason=next_requirement.reason,
            options=[
                QuestionOption(label="1 bedroom", value="1"),
                QuestionOption(label="2 bedrooms", value="2"),
                QuestionOption(label="3 bedrooms", value="3"),
                QuestionOption(label="4 bedrooms", value="4"),
            ],
        )

    elif field == "bathrooms":
        question = AdaptiveQuestion(
            field="bathrooms",
            question="How many bathrooms would you like?",
            priority="medium",
            reason=next_requirement.reason,
            options=[
                QuestionOption(label="1 bathroom", value="1"),
                QuestionOption(label="2 bathrooms", value="2"),
                QuestionOption(label="3 bathrooms", value="3"),
            ],
        )

    elif field == "kitchen":
        question = AdaptiveQuestion(
            field="kitchen",
            question="How many kitchens do you need?",
            priority="medium",
            reason=next_requirement.reason,
            options=[
                QuestionOption(label="1 kitchen", value="1"),
                QuestionOption(label="2 kitchens", value="2"),
            ],
        )

    elif field == "living_room":
        question = AdaptiveQuestion(
            field="living_room",
            question="How many living rooms would you like?",
            priority="medium",
            reason=next_requirement.reason,
            options=[
                QuestionOption(label="1 living room", value="1"),
                QuestionOption(label="2 living rooms", value="2"),
            ],
        )

    elif field == "parking":
        question = AdaptiveQuestion(
            field="parking",
            question="Would you like parking for the house?",
            priority="low",
            reason=next_requirement.reason,
            options=[
                QuestionOption(
                    label="Yes",
                    value="true",
                ),
                QuestionOption(
                    label="No",
                    value="false",
                ),
            ],
        )

    else:
        question = AdaptiveQuestion(
            field=field,
            question=f"Please specify your {field}.",
            priority=next_requirement.priority,
            reason=next_requirement.reason,
        )

    return QuestionResponse(
        question=question,
        completed=False,
    )