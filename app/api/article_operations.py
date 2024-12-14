from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..database.models import OnlineArticles
from datetime import datetime

def get_user_articles(
    db: Session, 
    profile_id: int,
    limit: int = 50  # Adding a limit for safety
) -> List[OnlineArticles]:
    """
    Get articles for a user profile with basic pagination.
    Returns the articles in chronological order (newest first).
    """
    try:
        articles = db.query(OnlineArticles)\
            .filter(OnlineArticles.profile_id == profile_id)\
            .order_by(desc(OnlineArticles.created_at))\
            .limit(limit)\
            .all()
        return articles
    except Exception as e:
        print(f"Database error in get_user_articles: {str(e)}")  # We'll replace with proper logging later
        return []