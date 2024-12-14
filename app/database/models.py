from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
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
    
class Profile(Base):
    __tablename__ = 'profiles'

    # Primary Data
    id = Column(Integer,primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(50),nullable=True)
    bio = Column(Text, nullable=True) # General description of the user
    interests_description = Column(Text,nullable=False) # Detailed description of the user
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    
class OnlineArticles(Base):
    __tablename__ = 'online_articles'

    id = Column(Integer,primary_key=True)
    profile_id = Column(Integer,ForeignKey('profiles.id'), nullable=False)
    url = Column(String(500),nullable=False)
    title = Column(Text,nullable=True)
    source_blog = Column(String(200), nullable=True)
    profile_fit = Column(Boolean,nullable=True) # Does it fit the user profile or not?
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))

    
