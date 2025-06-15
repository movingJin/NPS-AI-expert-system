from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from db.database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False)
    messages = Column(Text, nullable=False)
    docs = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())