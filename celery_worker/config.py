import os
from celery import Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('DATABASE_URL')

celery_app = Celery(
    'content_processor',     # Name of your application
    broker=CELERY_BROKER_URL,     # URL for the message broker (Redis/RabbitMQ)
    backend=CELERY_RESULT_BACKEND,  # Where to store task results (Supabase)
    include=['celery_worker.tasks']  # Python modules to import when workers start
)