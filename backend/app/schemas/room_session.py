from pydantic import BaseModel, Field

from app.schemas.room import RoomRequirements
from app.schemas.room_recommendation import (
    RoomRecommendation,
    FieldSource,
)


class RoomSessionState(BaseModel):

    session_id: str

    requirements: RoomRequirements = Field(
        default_factory=RoomRequirements
    )

    recommendations: dict[str, RoomRecommendation] = Field(
        default_factory=dict
    )

    field_sources: dict[str, FieldSource] = Field(
        default_factory=dict
    )