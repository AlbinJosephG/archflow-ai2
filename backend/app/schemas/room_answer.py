
from typing import Union

from pydantic import BaseModel


RoomAnswerValue = Union[
    str,
    int,
    float,
    bool,
    list[str],
    None,
]


class ParsedRoomAnswer(BaseModel):
    field: str
    value: RoomAnswerValue = None
    dimension_unit: str | None = None
