from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from .database import Base
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship 

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True)
    type = Column(Integer,nullable=False)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'), nullable=False)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    input_variables = Column(Text, nullable=True)  # Stored as JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    user = relationship('User',back_populates='prompts')
    
class Profile(Base):
    __tablename__ = 'profiles'

    # Primary Data
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    username = Column(String(50), unique=True, nullable=True)
    full_name = Column(String(50),nullable=True)
    bio = Column(Text, nullable=True) # General description of the user
    interests_description = Column(Text,nullable=False) # Detailed description of the user
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    user = relationship('User',back_populates='profile')
    
class OnlineArticles(Base):
    __tablename__ = 'online_articles'

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    url = Column(String(500),nullable=False)
    title = Column(Text,nullable=True)
    source_blog = Column(String(200), nullable=True)
    profile_fit = Column(Boolean,nullable=True) # Does it fit the user profile or not?
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    user = relationship('User', back_populates='online_articles')

class User(Base,UserMixin):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True)
    openai_api_key = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    profile = relationship('Profile',back_populates='user', uselist=False)
    prompts = relationship('Prompt',back_populates='user')
    online_articles = relationship('OnlineArticles', back_populates='user')
    is_onboarded = Column(Boolean,default=False,nullable=True)
        
    def set_password(self, password, method='pbkdf2:sha256'):
        self.password_hash = generate_password_hash(password, method=method)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)