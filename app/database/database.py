from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"sqlite:////Users/anastasiosanastasiadis/Desktop/coding/build_audience/instance/prompts.db"
DATABASE_URL = os.environ.get('DATABASE_URL')
# Create engine
engine = create_engine(
    DATABASE_URL
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 1. Create the base
Base = declarative_base()

def init_db():
    # Import models here to ensure they are known to SQLAlchemy
    from .models import Prompt, User, Profile, OnlineArticles
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()