from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnswerBase(BaseModel):
    topic: str
    messages: str
    docs: Optional[str] = None


class AnswerCreate(AnswerBase):
    pass


class AnswerSchema(AnswerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True