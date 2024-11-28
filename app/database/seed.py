from .database import SessionLocal, init_db, get_db , engine
from .models import Prompt, Base
import json


def seed_initial_prompt():

    template = """
    Using the following content:

    {content}

    The post should follow the following guidelines on structure:

    STRUCTURE GUIDELINES:

    THREAD STRUCTURE:

    1. Hook (First Tweet)
    - Purpose: Grab attention and entice readers
    - Format: Bold statement or compelling question
    - Focus: Value proposition or key benefit
    - Length: Keep under 280 chars
    - Style: Concise, impactful language

    2. Body (Middle Tweets) 
    - Purpose: Deliver key information
    - Format: Break into digestible points
    - Style: Clear, readable sentences
    - Flow: Natural progression between tweets
    - Length: Each tweet under 280 chars

    3. Call-to-Action (Final Tweet)
    - Purpose: Drive engagement
    - Format: Clear directive
    - Examples: "Share thoughts" or "Follow for more"
    - Alignment: Match thread content
    - Length: Under 280 chars

    REQUIREMENTS:
    - Create multi-tweet thread
    - Each tweet max 280 characters
    - Return plain text tweets in sequence
    - No formatting or metadata
    - No explanations/commentary
    - Verify character count per tweet
        """
    init_db()
    db = SessionLocal()

    try:
        existing_prompt = db.query(Prompt).first()
        if not existing_prompt:
            prompt = Prompt(
                name="Tweet Thread Generator",
                description="Generates viral tweet threads from article content",
                template=template,
                input_variables=json.dumps(["content"]),
                is_active=True               
            )
            db.add(prompt)
            db.commit()
            print("initial prompt seeded successfully!")
        else:
            print("Prompt already exists in database!")
    finally:
        db.close() 

if __name__ == "__main__":
    seed_initial_prompt()