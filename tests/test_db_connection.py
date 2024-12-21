from app.database.database import init_db, SessionLocal
from app.database.models import User

def test_connection():
    try:
        # Try to create all tables
        init_db()
        
        # Test connection by creating a session
        db = SessionLocal()
        
        # Try a simple query
        users = db.query(User).all()
        print("✅ Database connection successful!")
        print(f"Found {len(users)} users in database")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()