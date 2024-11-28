from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from .database import Base
from datetime import datetime, timezone

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    input_variables = Column(Text, nullable=False)  # Stored as JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))