import logging.config
import time
from datetime import datetime, timedelta

import pytz
from celery import Celery
from logging_config import logging_config

logging.config.dictConfig(logging_config)

task_logger = logging.getLogger('lesson_tasks')

MOSCOW_TZ = pytz.timezone('Europe/Moscow')

app = Celery(
    'lesson_worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/1',
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)


@app.task(bind=True, name='lesson.schedule_reminder')
def schedule_lesson_reminder(self, lesson_data):
    """
    Планирует напоминание за 5 минут до урока.
    Если до урока <5 минут — уведомление сразу.
    """
    task_id = self.request.id
    lesson_title = lesson_data.get('title')
    start_time = lesson_data.get("start_time")

    # Приводим к aware datetime в московской TZ
    if start_time.tzinfo is None:
        start_time = MOSCOW_TZ.localize(start_time)

    current_time = datetime.now(MOSCOW_TZ)

    # Логирование факта добавления в урок
    task_logger.info(f"[{task_id}] 📅 Вы добавлены в урок '{lesson_title}'. Время начала: {start_time.strftime('%Y-%m-%d %H:%M')}")

    # Вычисляем время для напоминания за 5 минут
    reminder_time = start_time - timedelta(minutes=5)
    seconds_to_wait = (reminder_time - current_time).total_seconds()

    task_logger.info(f"[{task_id}] ⏰ Напоминание должно прийти: {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")

    if seconds_to_wait > 0:
        # Отложенное уведомление за 5 минут
        task_logger.info(f"[{task_id}] ⏰ Планируем напоминание за 5 минут")
        send_lesson_reminder.apply_async(
            args=[lesson_title, start_time.isoformat(), True],
            countdown=seconds_to_wait
        )
    else:
        # До урока меньше 5 минут — уведомление сразу
        task_logger.info(f"[{task_id}] ⏰ Урок начнется менее чем через 5 минут, уведомление отправляем сразу")
        send_lesson_reminder.apply_async(
            args=[lesson_title, start_time.isoformat(), False],
            countdown=1
        )


@app.task(bind=True, name='lesson.send_reminder')
def send_lesson_reminder(self, lesson_title, start_time_iso, is_early_notice=True):
    """
    Логирует уведомление о уроке.
    is_early_notice=True — уведомление за 5 минут до урока
    is_early_notice=False — уведомление сразу, урок начнется скоро
    """
    task_id = self.request.id
    start_time = datetime.fromisoformat(start_time_iso)
    if start_time.tzinfo is None:
        start_time = MOSCOW_TZ.localize(start_time)

    if is_early_notice:
        message = f"🚨 Напоминание: через 5 минут начнется урок '{lesson_title}'. Время начала: {start_time.strftime('%Y-%m-%d %H:%M')}"
    else:
        message = f"🚨 Урок '{lesson_title}' начнется менее чем через 5 минут. Время начала: {start_time.strftime('%Y-%m-%d %H:%M')}"

    task_logger.info(f"[{task_id}] {message}")

    # Симуляция отправки уведомления
    time.sleep(1)

    return {'status': 'sent'}

