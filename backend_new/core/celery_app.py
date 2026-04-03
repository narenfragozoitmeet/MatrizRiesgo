"""Celery App - Configuración de tareas asincrónicas"""

from celery import Celery
from celery.schedules import crontab
from core.config import settings

# Crear app Celery
celery_app = Celery(
    "riesgo_ia",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.ingestion_tasks",
        "tasks.update_tasks"
    ]
)

# Configuración
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutos
    task_soft_time_limit=1500,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Tareas programadas (Celery Beat)
celery_app.conf.beat_schedule = {
    "update-normativas-monthly": {
        "task": "tasks.update_tasks.update_normativas",
        "schedule": crontab(day_of_month="1", hour="2", minute="0"),  # 2 AM el día 1 de cada mes
    },
    "update-catalogos-weekly": {
        "task": "tasks.update_tasks.update_catalogos",
        "schedule": crontab(day_of_week="0", hour="3", minute="0"),  # 3 AM todos los domingos
    },
    "learn-from-matrices-daily": {
        "task": "tasks.update_tasks.learn_from_matrices",
        "schedule": crontab(hour="1", minute="0"),  # 1 AM todos los días
    },
}

if __name__ == "__main__":
    celery_app.start()