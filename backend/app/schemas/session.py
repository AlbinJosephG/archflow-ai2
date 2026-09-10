from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.building import BuildingRequirements
from app.schemas.question import AdaptiveQuestion

class ConversationSession(BaseModel):
    session_id: str
    requirements: BuildingRequirements


    question_history: list[str] = Field(
        default_factory=list
    )

    pending_recommendation: dict[str, Any] | None = None


class CreateSessionRequest(BaseModel):
    description: str

class SessionResponse(BaseModel):
    session_id: str
    requirements: BuildingRequirements
    question: Optional[AdaptiveQuestion] = None
    completed: bool = False
