from app.database.database import SessionLocal, init_db
from app.database.models import User

def test_create_user():
    init_db()
    db = SessionLocal()
    
    # Create a test user
    test_user = User(
        email='1@example.com',
        is_active=True  # Explicitly set is_active
    )
    test_user.set_password('12345678')

    try:
        db.add(test_user)
        db.commit()
        print("✅ User created successfully!")
        user = db.query(User).filter_by(email='1@example.com').first()
        if user and user.check_password('12345678'):
            print("✅ Password verification works!")
            print(f"✅ User active status: {user.is_active}")
        else:
            print("❌ Password verification failed!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
if __name__ == '__main__':
    test_create_user()
        