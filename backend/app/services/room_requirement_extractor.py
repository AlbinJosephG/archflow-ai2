
import json
import requests

from app.schemas.room import RoomRequirements


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def extract_json(text: str):
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError("No valid JSON found in LLM response")

    json_text = text[start:end]

    return json.loads(json_text)


def extract_room_requirements(description: str):

    prompt = f"""
You are a strict interior architecture requirement extraction system.

Your ONLY task is to extract information explicitly stated by the user.

CRITICAL RULES:

1. NEVER guess or infer information.
2. NEVER invent room dimensions.
3. NEVER assume furniture that the user has not mentioned.
4. NEVER convert words like small, large, spacious or compact
   into numerical dimensions.
5. If a field is not explicitly mentioned, return null.
6. For furniture, return only explicitly mentioned furniture items.
7. Return ONLY valid JSON. No explanation or markdown.

Use exactly these fields:

room_type
room_width
room_length
room_height
dimension_unit
style
wall_material
wall_color
flooring_material
ceiling_type
door_count
window_count
furniture
lighting_preference
special_requirements

FIELD RULES:

- room_type:
  Extract the room type, such as living room, bedroom,
  kitchen, dining room or office.

- room_width:
  Extract the explicitly mentioned room width as a number.

- room_length:
  Extract the explicitly mentioned room length as a number.

- room_height:
  Extract the explicitly mentioned room height as a number.

- dimension_unit:
  Extract the unit explicitly associated with dimensions.
  Examples: feet, meters, inches.

- style:
  Extract the requested interior design style.
  Examples: modern, minimalist, traditional, contemporary.

- wall_material:
  Extract explicitly mentioned wall materials.
  Examples: brick, concrete, wood, wallpaper.

- wall_color:
  Extract explicitly mentioned wall colours.

- flooring_material:
  Extract explicitly mentioned flooring materials.
  Examples: marble, wooden flooring, tiles.

- ceiling_type:
  Extract explicitly mentioned ceiling preferences.
  Examples: false ceiling, wooden ceiling, plain ceiling.

- door_count:
  Extract the explicitly mentioned number of doors.

- window_count:
  Extract the explicitly mentioned number of windows.

- furniture:
  Return a JSON array of explicitly mentioned furniture items.
  If none are mentioned, return an empty array.

- lighting_preference:
  Extract explicitly mentioned lighting preferences.
  Examples: warm lighting, natural lighting, LED lighting.

- special_requirements:
  Extract other explicitly stated room requirements.
  If none are mentioned, return null.

IMPORTANT:

If the user says:
"Create a modern living room with a sofa and television"

Extract:
room_type = "living room"
style = "modern"
furniture = ["sofa", "television"]

Do not invent dimensions, doors, windows or other furniture.

Return this exact JSON structure:

{{
    "room_type": null,
    "room_width": null,
    "room_length": null,
    "room_height": null,
    "dimension_unit": null,
    "style": null,
    "wall_material": null,
    "wall_color": null,
    "flooring_material": null,
    "ceiling_type": null,
    "door_count": null,
    "window_count": null,
    "furniture": [],
    "lighting_preference": null,
    "special_requirements": null
}}

USER DESCRIPTION:

{description}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    llm_output = result["response"]

    data = extract_json(llm_output)

    requirements = RoomRequirements(**data)

    return requirements


def interpret_room_answer(field: str, answer: str):
    """
    Use Qwen only when the Python parser cannot confidently
    interpret the user's answer.

    Returns structured JSON containing one or more answers.
    """

    prompt = f"""
You are an assistant that interprets answers to room design questions.

The currently requested field is: {field}

The user's answer is:
{answer}

Allowed fields:
room_type
room_width
room_length
room_height
dimension_unit
style
wall_material
wall_color
flooring_material
ceiling_type
door_count
window_count
furniture
lighting_preference
special_requirements

STRICT RULES:

1. Extract only information explicitly provided by the user.
2. Never guess or invent missing values.
3. Extract multiple fields if the user explicitly mentions them.
4. For dimensions, return numeric values.
5. Use dimension_unit values: feet, meters, or inches.
6. For furniture, return a list of strings.
7. For door_count and window_count, return integers.
8. Do not interpret approximate descriptions as exact values
   unless the user explicitly provides a numerical measurement.
9. If the answer is ambiguous, incomplete, or contradictory,
   set needs_clarification to true.
10. The currently requested field must be present in answers
    unless clarification is required.
11. Do not return fields that the user did not explicitly mention.
12. Return JSON only.

For a clear answer, use this structure:

{{
    "needs_clarification": false,
    "clarification_question": null,
    "answers": [
        {{
            "field": "room_width",
            "value": 12,
            "dimension_unit": "feet"
        }}
    ]
}}

For an ambiguous answer, use:

{{
    "needs_clarification": true,
    "clarification_question": "Could you clarify the room width?",
    "answers": []
}}

If the user says:
"The room is twelve feet wide, fifteen feet long,
and twenty feet high."

Return all three dimensions.

USER ANSWER:
{answer}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()
        data = extract_json(result["response"])

        if not isinstance(data, dict):
            raise ValueError("Invalid LLM response format")

        return data

    except requests.RequestException as error:
        raise RuntimeError(
            f"Qwen answer interpretation failed: {error}"
        ) from error

def interpret_room_answer(field: str, answer: str):

    prompt = f"""
You are an assistant that interprets architectural room requirements.

CURRENT QUESTION FIELD: {field}

USER ANSWER:
"{answer}"

Your task is to interpret the user's answer ONLY for the CURRENT QUESTION FIELD.

STRICT RULES:

1. Return exactly ONE answer for the current field.
2. Never extract multiple fields.
3. Never ask about another missing room requirement.
4. Never use previous conversation context to change the current field.
5. Extract only information explicitly provided by the user.
6. Understand natural language and number words.
   Examples:
   - twelve = 12
   - fifteen = 15
   - twenty = 20
7. For dimensions, extract numeric values and measurement units if provided.
8. For door_count and window_count, return integers.
9. For furniture, return a list of strings.
10. For text fields, return a concise string preserving the user's meaning.
11. If the answer is unclear or does not answer the current field,
    request clarification about the CURRENT FIELD ONLY.
12. Do not invent missing values.

FIELD-SPECIFIC EXAMPLES:

Current field: room_width
User answer: "twelve"
Output:
{{
    "needs_clarification": false,
    "clarification_question": null,
    "answers": [
        {{
            "field": "room_width",
            "value": 12,
            "dimension_unit": null
        }}
    ]
}}

Current field: ceiling_type
User answer: "false ceiling"
Output:
{{
    "needs_clarification": false,
    "clarification_question": null,
    "answers": [
        {{
            "field": "ceiling_type",
            "value": "false ceiling"
        }}
    ]
}}

Current field: style
User answer: "modern minimalist"
Output:
{{
    "needs_clarification": false,
    "clarification_question": null,
    "answers": [
        {{
            "field": "style",
            "value": "modern minimalist"
        }}
    ]
}}

Current field: ceiling_type
User answer: "I don't know"
Output:
{{
    "needs_clarification": true,
    "clarification_question": "What type of ceiling would you prefer?",
    "answers": []
}}

Return ONLY valid JSON.

SUCCESS FORMAT:
{{
    "needs_clarification": false,
    "clarification_question": null,
    "answers": [
        {{
            "field": "{field}",
            "value": "extracted value"
        }}
    ]
}}

CLARIFICATION FORMAT:
{{
    "needs_clarification": true,
    "clarification_question": "Ask about the current field only",
    "answers": []
}}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        return extract_json(result["response"])

    except requests.RequestException as error:
        raise RuntimeError(
            f"Could not connect to Ollama: {error}"
        ) from error