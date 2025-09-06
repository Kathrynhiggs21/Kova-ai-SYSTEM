import os
from celery import Celery
from datetime import datetime

broker = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://redis:6379/0"))
backend = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://redis:6379/0"))
celery_app = Celery("kova", broker=broker, backend=backend, include=["app.tasks.celery_app"])

@celery_app.task(name="kova.ping")
def ping():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}

celery_app.conf.beat_schedule = {"ping-every-60s": {"task":"kova.ping","schedule":60.0}}
