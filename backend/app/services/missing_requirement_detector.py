from typing import List

from pydantic import BaseModel

from app.schemas.building import BuildingRequirements


class MissingRequirement(BaseModel):
    field: str
    priority: str
    reason: str


class MissingRequirementsResponse(BaseModel):
    missing_requirements: List[MissingRequirement]


def detect_missing_requirements(
    requirements: BuildingRequirements,
) -> MissingRequirementsResponse:

    missing = []

    # ---------------------------------------------------------
    # 1. Plot dimensions
    # ---------------------------------------------------------

    if (
        requirements.plot_width is None
        or requirements.plot_length is None
    ):
        missing.append(
            MissingRequirement(
                field="plot_dimensions",
                priority="high",
                reason=(
                    "Plot dimensions are needed to generate "
                    "a valid floor layout."
                ),
            )
        )

    # ---------------------------------------------------------
    # 2. Number of floors
    # ---------------------------------------------------------

    if requirements.floors is None:
        missing.append(
            MissingRequirement(
                field="floors",
                priority="high",
                reason=(
                    "The number of floors affects "
                    "vertical room distribution."
                ),
            )
        )

    # ---------------------------------------------------------
    # 3. Number of bedrooms
    # ---------------------------------------------------------

    if requirements.bedrooms is None:
        missing.append(
            MissingRequirement(
                field="bedrooms",
                priority="high",
                reason=(
                    "Bedroom count affects the number "
                    "and arrangement of rooms."
                ),
            )
        )

    # ---------------------------------------------------------
    # 4. Number of bathrooms
    # ---------------------------------------------------------

    if requirements.bathrooms is None:
        missing.append(
            MissingRequirement(
                field="bathrooms",
                priority="medium",
                reason=(
                    "Bathroom requirements affect "
                    "room allocation and plumbing layout."
                ),
            )
        )

    # ---------------------------------------------------------
    # 5. Kitchen
    # ---------------------------------------------------------

    if requirements.kitchen is None:
        missing.append(
            MissingRequirement(
                field="kitchen",
                priority="medium",
                reason=(
                    "Kitchen requirements affect "
                    "functional room placement."
                ),
            )
        )

    # ---------------------------------------------------------
    # 6. Living room
    # ---------------------------------------------------------

    if requirements.living_room is None:
        missing.append(
            MissingRequirement(
                field="living_room",
                priority="medium",
                reason=(
                    "Living room requirements affect "
                    "common-space allocation."
                ),
            )
        )

    # ---------------------------------------------------------
    # 7. Parking
    # ---------------------------------------------------------

    if requirements.parking is None:
        missing.append(
            MissingRequirement(
                field="parking",
                priority="low",
                reason=(
                    "Parking requirements affect "
                    "the external site layout."
                ),
            )
        )

    # ---------------------------------------------------------
    # Return result
    # ---------------------------------------------------------

    return MissingRequirementsResponse(
        missing_requirements=missing
    )