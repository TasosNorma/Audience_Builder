from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import User, Profile, Prompt, OnlineArticles
import os

# Old SQLite connection
SQLITE_URL = "sqlite:////Users/anastasiosanastasiadis/Desktop/coding/build_audience/instance/prompts.db"
old_engine = create_engine(SQLITE_URL)
OldSession = sessionmaker(bind=old_engine)

# New Supabase connection (using existing configuration)
from app.database.database import SessionLocal as NewSession, init_db

def migrate_data():
    old_db = OldSession()
    new_db = NewSession()
    
    try:
        # 1. Migrate Users first (since other tables depend on users)
        print("Migrating users...")
        users = old_db.query(User).all()
        for user in users:
            new_user = User(
                id=user.id,  # Keep same IDs for referential integrity
                email=user.email,
                password_hash=user.password_hash,
                is_active=user.is_active,
                openai_api_key=user.openai_api_key,
                created_at=user.created_at,
                is_onboarded=user.is_onboarded
            )
            new_db.add(new_user)
        new_db.commit()
        print(f"✅ Migrated {len(users)} users")

        # 2. Migrate Profiles
        print("Migrating profiles...")
        profiles = old_db.query(Profile).all()
        for profile in profiles:
            new_profile = Profile(
                id=profile.id,
                user_id=profile.user_id,
                full_name=profile.full_name,
                bio=profile.bio,
                interests_description=profile.interests_description,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
            new_db.add(new_profile)
        new_db.commit()
        print(f"✅ Migrated {len(profiles)} profiles")

        # 3. Migrate Prompts
        print("Migrating prompts...")
        prompts = old_db.query(Prompt).all()
        for prompt in prompts:
            new_prompt = Prompt(
                id=prompt.id,
                user_id=prompt.user_id,
                name=prompt.name,
                template=prompt.template,
                type=prompt.type,
                created_at=prompt.created_at,
                updated_at=prompt.updated_at
            )
            new_db.add(new_prompt)
        new_db.commit()
        print(f"✅ Migrated {len(prompts)} prompts")

        # 4. Migrate Online Articles
        print("Migrating online articles...")
        articles = old_db.query(OnlineArticles).all()
        for article in articles:
            new_article = OnlineArticles(
                id=article.id,
                user_id=article.user_id,
                url=article.url,
                title=article.title,
                source_blog=article.source_blog,
                profile_fit=article.profile_fit,
                created_at=article.created_at,
                updated_at=article.updated_at
            )
            new_db.add(new_article)
        new_db.commit()
        print(f"✅ Migrated {len(articles)} articles")

        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        new_db.rollback()
        print(f"❌ Error during migration: {str(e)}")
    finally:
        old_db.close()
        new_db.close()

if __name__ == "__main__":
    # Create tables in Supabase first
    print("Creating tables in Supabase...")
    init_db()
    
    # Start migration
    print("Starting migration...")
    migrate_data()