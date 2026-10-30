
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.room import RoomRequirements
from app.schemas.question import AdaptiveQuestion
from app.schemas.room_recommendation import (
    RoomRecommendation,
    FieldSource,
)


SessionType = Literal["room"]


class ConversationSession(BaseModel):
    session_id: str

    # ArchFlow AI now supports room sessions only.
    session_type: SessionType = "room"

    requirements: RoomRequirements

    # Conversation tracking
    question_history: list[str] = Field(default_factory=list)
    active_question: str | None = None

    # Recommendation tracking
    pending_recommendation: dict[str, Any] | None = None

    recommendations: dict[str, RoomRecommendation] = Field(
        default_factory=dict
    )

    field_sources: dict[str, FieldSource] = Field(
        default_factory=dict
    )


class CreateSessionRequest(BaseModel):
    description: str


class SessionResponse(BaseModel):
    session_id: str
    session_type: SessionType = "room"
    requirements: RoomRequirements
    question: Optional[AdaptiveQuestion] = None
    completed: bool = False
