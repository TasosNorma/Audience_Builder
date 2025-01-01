from celery_worker.config import celery_app
from app.core.content_processor import SyncAsyncContentProcessor
from app.database.database import SessionLocal
from app.database.models import User, ProcessingResult
from datetime import datetime, timezone
import json

@celery_app.task(bind=True)
def process_url_task(self,url:str,user_id:int):
    db = SessionLocal()
    try:
        try:
            user = db.query(User).get(user_id)
        except Exception as e:
            print(f"Error getting user {user_id}: {str(e)}")
            raise
        try:
            processor = SyncAsyncContentProcessor(user)
            result = processor.process_url(url)
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
            raise

        # Store result in database
        processing_result = ProcessingResult(
            user_id=user_id,
            url=url,
            status=result["status"],
            tweets=json.dumps(result.get("tweets", [])),
            tweet_count=result.get("tweet_count", 0),
            error_message=result.get("message", None),
            task_id=self.request.id,
            created_at=datetime.now(timezone.utc)
        )
        db.add(processing_result)
        db.commit()
        
        return {
            "status": "success",
            "task_id": self.request.id,
            "result_id": processing_result.id
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

