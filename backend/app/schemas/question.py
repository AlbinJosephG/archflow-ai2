from typing import List, Optional
from pydantic import BaseModel


class QuestionOption(BaseModel):
    label: str
    value: str


class AdaptiveQuestion(BaseModel):
    field: str
    question: str
    priority: str
    reason: str
    options: Optional[List[QuestionOption]] = None


class QuestionResponse(BaseModel):
    question: Optional[AdaptiveQuestion] = None
    completed: bool