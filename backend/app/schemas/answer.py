from pydantic import BaseModel
from typing import Union


class UserAnswer(BaseModel):
    answer: str


class ParseAnswerRequest(BaseModel):
    field: str
    answer: str


class ParsedAnswer(BaseModel):
    field: str

    value: str | int | float | bool | None = None
    plot_width: float | None = None
    plot_length: float | None = None
    plot_unit: str | None = None

class RecommendationAcceptance(BaseModel):
    accept: bool