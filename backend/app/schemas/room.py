
from typing import List, Optional

from pydantic import BaseModel, Field


class RoomRequirements(BaseModel):
    # Room identification
    room_type: Optional[str] = None

    # Room dimensions
    room_width: Optional[float] = Field(default=None, gt=0)
    room_length: Optional[float] = Field(default=None, gt=0)
    room_height: Optional[float] = Field(default=None, gt=0)
    dimension_unit: Optional[str] = None

    # Interior design
    style: Optional[str] = None
    wall_material: Optional[str] = None
    wall_color: Optional[str] = None
    flooring_material: Optional[str] = None
    ceiling_type: Optional[str] = None

    # Openings
    door_count: Optional[int] = Field(default=None, ge=0)
    window_count: Optional[int] = Field(default=None, ge=0)

    # Interior elements
    furniture: List[str] = Field(default_factory=list)
    lighting_preference: Optional[str] = None

    # Other explicitly stated requirements
    special_requirements: Optional[str] = None


class RoomRequest(BaseModel):
    description: str
