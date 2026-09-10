import json
import requests

from app.schemas.building import BuildingRequirements


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "qwen2.5:3b"


def extract_json(text: str):

    text = text.strip()

    start = text.find("{")

    end = text.rfind("}") + 1

    if start == -1 or end == 0:

        raise ValueError(
            "No valid JSON found in LLM response"
        )

    json_text = text[start:end]

    return json.loads(json_text)


def extract_requirements(description: str):

    prompt = f"""
You are a strict architectural requirement extraction system.

Your ONLY job is to extract information explicitly stated by the user.

CRITICAL RULES:

1. NEVER guess or infer information.
2. NEVER calculate missing requirements.
3. NEVER assume a value based on common architectural practices.
4. NEVER convert family size into number of bedrooms.
5. NEVER convert words like "small", "large", "spacious", or "compact"
   into numerical dimensions.
6. If a field is not explicitly mentioned, return null.
7. If the user says "five people", this means family_size = 5.
   It does NOT mean bedrooms = 5.
8. If the user says "three bedrooms", bedrooms = 3.
9. If the user says "two-floor house", floors = 2.
10. Return ONLY valid JSON. No explanation, no markdown.

Use exactly these fields:

building_type
family_size
plot_width
plot_length
plot_unit
floors
bedrooms
bathrooms
kitchen
living_room
parking
style

FIELD RULES:

- building_type:
  Extract the type of building explicitly mentioned.
  Examples: house, apartment, villa, office.

- family_size:
  Number of people explicitly mentioned.

- plot_width:
  Numerical plot width explicitly mentioned.

- plot_length:
  Numerical plot length explicitly mentioned.

- plot_unit:
  Unit explicitly associated with plot dimensions.
  Examples: feet, meters.

- floors:
  Number of floors explicitly mentioned.

- bedrooms:
  Number of bedrooms explicitly mentioned.

- bathrooms:
  Number of bathrooms explicitly mentioned.

- kitchen:
  Only extract a numeric value if the user explicitly specifies
  the number of kitchens.
  Otherwise null.

- living_room:
  Only extract a numeric value if the user explicitly specifies
  the number of living rooms.
  Otherwise null.

- parking:
  Set true if the user explicitly mentions, requests, wants,
  includes, or requires parking.

  Examples:
  "I want parking" → true
  "Include parking" → true
  "The house should have parking" → true
  "Parking for two cars" → true
  "with parking" → true

  Set false only if the user explicitly says:
  "I don't want parking"
  "No parking"
  "without parking"

  Otherwise return null.

  IMPORTANT:
  The word "parking" anywhere in the user's architectural
  requirements means parking is explicitly mentioned.
  

- style:
  Extract the architectural style explicitly mentioned.
  Examples: modern, traditional, contemporary, minimalist.

User description:

{description}
"""

    payload = {

        "model": MODEL_NAME,

        "prompt": prompt,

        "stream": False

    }


    response = requests.post(

        OLLAMA_URL,

        json=payload

    )


    response.raise_for_status()


    result = response.json()


    llm_output = result["response"]


    data = extract_json(
        llm_output
    )


    requirements = BuildingRequirements(
        **data
    )


    return requirements