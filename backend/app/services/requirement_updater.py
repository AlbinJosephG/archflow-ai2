from app.schemas.building import BuildingRequirements
from app.schemas.answer import ParsedAnswer


def update_requirements(
    requirements: BuildingRequirements,
    parsed_answer: ParsedAnswer,
) -> BuildingRequirements:

    field = parsed_answer.field

    # --------------------------------
    # Plot dimensions
    # --------------------------------

    if field == "plot_dimensions":

        if parsed_answer.plot_width is not None:
            requirements.plot_width = parsed_answer.plot_width

        if parsed_answer.plot_length is not None:
            requirements.plot_length = parsed_answer.plot_length

        if parsed_answer.plot_unit is not None:
            requirements.plot_unit = parsed_answer.plot_unit

    # --------------------------------
    # Numeric fields
    # --------------------------------

    elif field in [
        "floors",
        "bedrooms",
        "bathrooms",
        "kitchen",
        "living_room",
    ]:

        if parsed_answer.value is not None:

            value = int(parsed_answer.value)

            setattr(
                requirements,
                field,
                value,
            )

    # --------------------------------
    # Parking
    # --------------------------------

    elif field == "parking":

        if parsed_answer.value is not None:

            if parsed_answer.value == "true":
                requirements.parking = True

            elif parsed_answer.value == "false":
                requirements.parking = False

    return requirements