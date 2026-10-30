from typing import Any, Literal
from pydantic import BaseModel, Field


RecommendationStatus = Literal[
    "pending",
    "accepted",
    "rejected",
    "superseded",
]

FieldSource = Literal[
    "user_provided",
    "ai_recommendation_confirmed",
]


class RoomRecommendation(BaseModel):
    field: str
    value: Any
    reason: str

    source: Literal["ai"] = "ai"

    status: RecommendationStatus = "pending"


class RoomReadiness(BaseModel):
    brief_completed: bool

    scene_ready: bool

    missing_core_fields: list[str] = Field(
        default_factory=list
    )

    missing_scene_fields: list[str] = Field(
        default_factory=list
    )

    unconfirmed_scene_fields: list[str] = Field(
        default_factory=list
    )