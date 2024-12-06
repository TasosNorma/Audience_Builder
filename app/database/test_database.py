from database.database import SessionLocal
from database.models import Prompt

def test_print_first_template():
    db = SessionLocal()
    try:
        first_prompt = db.query(Prompt).first()
        if first_prompt:
            print(f"First template: {first_prompt.template}")
        else:
            print("No prompts found in database")
    finally:
        db.close()

if __name__ == "__main__":
    test_print_first_template()

