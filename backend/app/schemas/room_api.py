from pydantic import BaseModel, Field


class StartRoomRequest(BaseModel):
    description: str = Field(
        min_length=1,
        description="Description of the room to be designed."
    )


class SubmitRoomAnswerRequest(BaseModel):
    answer: str = Field(
        min_length=1,
        description="Answer to the current room question."
    )