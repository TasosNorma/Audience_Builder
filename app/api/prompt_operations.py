from typing import List, Optional
from ..database.database import SessionLocal
from ..database.models import Prompt
from datetime import datetime

def get_prompt(prompt_type: int, user_id: int) -> Optional[str]:
    db = SessionLocal()
    try:
        prompt = db.query(Prompt).filter(
            Prompt.type == prompt_type, 
            Prompt.user_id == user_id
        ).first()
        
        if prompt:
            print(f"Fetched the template from the database and the template is: {prompt.template[:50]}")
            return prompt.template
        return None
    except Exception as e:
        print(f"Error fetching prompt from database {str(e)}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Test get_prompt with user_id 3
    test_prompt = get_prompt(prompt_type=2, user_id=3)
    if test_prompt:
        print(f"Successfully retrieved prompt: {test_prompt[:100]}...")
    else:
        print("No prompt found for user_id 3")
