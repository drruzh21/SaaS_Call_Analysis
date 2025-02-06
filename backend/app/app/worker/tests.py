import time

from raven import Client

from app.core.celery_app import celery_app
from app.core.config import settings

client_sentry = Client(settings.SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    """
    Process text asynchronously using Celery.
    
    Args:
        word: Input text to process
        
    Returns:
        str: Processed text result
    """
    time.sleep(5)  # Simulating processing time
    return f"test task return {word}"
