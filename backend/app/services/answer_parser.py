import json
import re
import requests

from app.schemas.answer import UserAnswer, ParsedAnswer


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def extract_json(text: str):
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError("No valid JSON found in LLM response")

    return json.loads(text[start:end])


def word_to_number(text: str):
    numbers = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    text = text.lower()

    for word, number in numbers.items():
        if re.search(rf"\b{word}\b", text):
            return number

    return None


def parse_numeric_answer(answer: str):
    """
    Extract a single numeric value from natural language.
    Supports both digits and common number words.
    """

    # Try numerical digits first
    match = re.search(r"\b(\d+(?:\.\d+)?)\b", answer)

    if match:
        return match.group(1)

    # Try number words
    number = word_to_number(answer)

    if number is not None:
        return str(number)

    return None


def parse_parking_answer(answer: str):
    """
    Deterministically interpret parking yes/no answers.
    """

    text = answer.lower().strip()

    negative_patterns = [
        "no",
        "don't",
        "do not",
        "dont",
        "no parking",
        "without parking",
        "not want parking",
        "don't want parking",
        "do not want parking",
        "don't need parking",
        "do not need parking",
    ]

    for pattern in negative_patterns:
        if pattern in text:
            return "false"

    positive_patterns = [
        "yes",
        "parking",
        "want parking",
        "need parking",
        "include parking",
        "with parking",
    ]

    for pattern in positive_patterns:
        if pattern in text:
            return "true"

    return None

def parse_plot_dimensions(answer: str):
    """
    Extract plot width, length and unit.

    Supported examples:
    40 by 60 feet
    40 x 60 feet
    40 × 60 feet
    40 feet by 60 feet
    30m x 40m
    """

    text = answer.lower().strip()

    # Normalize multiplication symbols and "by"
    normalized = text.replace("×", "x")
    normalized = normalized.replace(" by ", " x ")

    # --------------------------------
    # Case 1:
    # 40 x 60 feet
    # 40 x 60 ft
    # 30 x 40 meters
    # --------------------------------

    pattern = (
        r"(\d+(?:\.\d+)?)"
        r"\s*x\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*"
        r"(feet|foot|ft|meters|meter|metres|metre|m)"
    )

    match = re.search(pattern, normalized)

    if match:
        width = float(match.group(1))
        length = float(match.group(2))
        unit = match.group(3)

        if unit in ["feet", "foot", "ft"]:
            unit = "feet"
        else:
            unit = "meters"

        return width, length, unit

    # --------------------------------
    # Case 2:
    # 40 feet x 60 feet
    # 40 feet by 60 feet
    # --------------------------------

    pattern_words = (
        r"(\d+(?:\.\d+)?)"
        r"\s*"
        r"(feet|foot|ft|meters|meter|metres|metre|m)"
        r"\s*x\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*"
        r"(feet|foot|ft|meters|meter|metres|metre|m)"
    )

    match = re.search(pattern_words, normalized)

    if match:
        width = float(match.group(1))
        length = float(match.group(3))

        unit = match.group(2)

        if unit in ["feet", "foot", "ft"]:
            unit = "feet"
        else:
            unit = "meters"

        return width, length, unit

    # --------------------------------
    # Case 3:
    # 40 feet by 60
    # 40 meters by 60
    # --------------------------------

    pattern_mixed = (
        r"(\d+(?:\.\d+)?)"
        r"\s*"
        r"(feet|foot|ft|meters|meter|metres|metre|m)"
        r"\s*x\s*"
        r"(\d+(?:\.\d+)?)"
    )

    match = re.search(pattern_mixed, normalized)

    if match:
        width = float(match.group(1))
        length = float(match.group(3))

        unit = match.group(2)

        if unit in ["feet", "foot", "ft"]:
            unit = "feet"
        else:
            unit = "meters"

        return width, length, unit

    return None, None, None


def parse_user_answer(
    field: str,
    answer: str,
) -> ParsedAnswer:

    # --------------------------------
    # Plot dimensions
    # --------------------------------

    if field == "plot_dimensions":

        width, length, unit = parse_plot_dimensions(answer)

        return ParsedAnswer(
            field=field,
            value=None,
            plot_width=width,
            plot_length=length,
            plot_unit=unit,
        )

    # --------------------------------
    # Parking
    # --------------------------------

    if field == "parking":

        value = parse_parking_answer(answer)

        return ParsedAnswer(
            field=field,
            value=value,
        )

    # --------------------------------
    # Numeric requirements
    # --------------------------------

    numeric_fields = [
        "floors",
        "bedrooms",
        "bathrooms",
        "kitchen",
        "living_room",
    ]

    if field in numeric_fields:

        value = parse_numeric_answer(answer)

        return ParsedAnswer(
            field=field,
            value=value,
        )

    # --------------------------------
    # Fallback to LLM
    # --------------------------------

    prompt = f"""
You are a strict architectural answer parser.

The system asked the user about:

{field}

The user's answer is:

{answer}

Extract ONLY the value explicitly provided by the user.

Never guess.

If the answer is unclear, return null.

Return ONLY valid JSON:

{{
    "field": "{field}",
    "value": null,
    "plot_width": null,
    "plot_length": null,
    "plot_unit": null
}}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
    )

    response.raise_for_status()

    result = response.json()

    llm_output = result["response"]

    data = extract_json(llm_output)

    return ParsedAnswer(**data)