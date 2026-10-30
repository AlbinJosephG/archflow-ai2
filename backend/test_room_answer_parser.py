
from app.services.room_answer_parser import parse_room_answer


test_cases = [
    ("room_height", "10 feet"),
    ("room_width", "12.5 meters"),
    ("door_count", "two"),
    ("window_count", "3"),
    ("style", "minimalist"),
    ("furniture", "sofa, television and coffee table"),
    ("lighting_preference", "warm lighting"),
]


for field, answer in test_cases:

    result = parse_room_answer(field, answer)

    print(f"\nInput: {answer}")
    print(result.model_dump())
