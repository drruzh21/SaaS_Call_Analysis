from celery import Celery

# Initialize Celery app
celery_app = Celery(
    "worker",
    broker="amqp://guest@queue//",
    include=[
        "app.worker.analyze_call"  # Include the analyze_call module
    ]
)

# Configure Celery
celery_app.conf.update(
    task_routes={"app.worker.*": "main-queue"},
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
