from celery import Celery

external_celery = Celery('external_client')

external_celery.conf.update(
    broker_url='redis://redis:6379/0',
    result_backend='redis://redis:6379/1',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)
