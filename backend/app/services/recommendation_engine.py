from app.schemas.building import BuildingRequirements


def recommend_floors(
    requirements: BuildingRequirements,
):
    """
    Recommend the number of floors based on
    family size and plot dimensions.
    """

    family_size = requirements.family_size
    plot_width = requirements.plot_width
    plot_length = requirements.plot_length

    plot_area = None

    if plot_width and plot_length:
        plot_area = plot_width * plot_length

    # Rule 1: Large family
    if family_size and family_size >= 7:

        return {
            "field": "floors",
            "recommended_value": 2,
            "reason": (
                "A two-floor layout is recommended because "
                "a larger family usually requires more living space."
            )
        }

    # Rule 2: Medium family + smaller plot
    if (
        family_size
        and family_size >= 4
        and plot_area
        and plot_area <= 1500
    ):

        return {
            "field": "floors",
            "recommended_value": 2,
            "reason": (
                "A two-floor layout is recommended to use "
                "the available plot area more efficiently."
            )
        }

    # Rule 3: Medium family
    if family_size and family_size >= 4:

        return {
            "field": "floors",
            "recommended_value": 2,
            "reason": (
                "A two-floor house is recommended to provide "
                "better separation between common and private spaces."
            )
        }

    # Default
    return {
        "field": "floors",
        "recommended_value": 1,
        "reason": (
            "A single-floor layout is recommended because "
            "it can provide a simple and efficient arrangement."
        )
    }


def recommend_bedrooms(
    requirements: BuildingRequirements,
):
    """
    Recommend bedroom count based on family size.
    """

    family_size = requirements.family_size

    if family_size is None:

        return {
            "field": "bedrooms",
            "recommended_value": 2,
            "reason": (
                "A two-bedroom layout is suggested as a "
                "general starting point."
            )
        }

    if family_size <= 2:

        bedrooms = 1

    elif family_size <= 4:

        bedrooms = 2

    elif family_size <= 6:

        bedrooms = 3

    else:

        bedrooms = 4

    return {
        "field": "bedrooms",
        "recommended_value": bedrooms,
        "reason": (
            f"A {bedrooms}-bedroom layout is recommended "
            f"for a family of {family_size} people."
        )
    }


def recommend_bathrooms(
    requirements: BuildingRequirements,
):
    """
    Recommend bathroom count based on family size
    and bedroom count.
    """

    family_size = requirements.family_size
    bedrooms = requirements.bedrooms

    if bedrooms and bedrooms >= 4:

        bathrooms = 3

    elif bedrooms and bedrooms >= 3:

        bathrooms = 2

    elif family_size and family_size >= 5:

        bathrooms = 2

    else:

        bathrooms = 1

    return {
        "field": "bathrooms",
        "recommended_value": bathrooms,
        "reason": (
            f"{bathrooms} bathroom(s) are recommended based on "
            "the current household and bedroom requirements."
        )
    }


def get_recommendation(
    field: str,
    requirements: BuildingRequirements,
):
    """
    Return a recommendation based on the field.
    """

    if field == "floors":

        return recommend_floors(requirements)

    if field == "bedrooms":

        return recommend_bedrooms(requirements)

    if field == "bathrooms":

        return recommend_bathrooms(requirements)

    return None

def is_recommendation_request(answer: str) -> bool:
    """
    Detect whether the user is asking the system
    to recommend a value.
    """

    if not answer:
        return False

    normalized = answer.strip().lower()

    recommendation_phrases = [
        "i don't know",
        "i dont know",
        "don't know",
        "dont know",
        "not sure",
        "i'm not sure",
        "im not sure",
        "recommend",
        "recommend for me",
        "you decide",
        "suggest",
        "suggest for me",
        "anything is fine",
    ]

    return any(
        phrase in normalized
        for phrase in recommendation_phrases
    )