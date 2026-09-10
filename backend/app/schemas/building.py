from typing import Optional

from pydantic import BaseModel
from app.schemas.answer import (
    UserAnswer,
    ParseAnswerRequest,
)

class BuildingRequirements(BaseModel):
    building_type: Optional[str] = None

    family_size: Optional[int] = None

    plot_width: Optional[float] = None

    plot_length: Optional[float] = None

    plot_unit: Optional[str] = None

    floors: Optional[int] = None

    bedrooms: Optional[int] = None

    bathrooms: Optional[int] = None

    kitchen: Optional[int] = None

    living_room: Optional[int] = None

    parking: Optional[bool] = None

    style: Optional[str] = None


class BuildingRequest(BaseModel):
    description: str