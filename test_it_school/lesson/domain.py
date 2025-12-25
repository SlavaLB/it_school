from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from lesson.forms import LessonCreateForm
from lesson.models import Lesson

from test_it_school.celery import external_celery


class LessonDomain:
    """
    Доменный сервис, содержащий чистую бизнес-логику приложения Lessons.

    Этот класс отвечает за реализацию бизнес-правил, валидацию данных
    и взаимодействие с внешними системами (БД, Celery). Не содержит
    логики представления или HTTP-обработки.

    """

    @staticmethod
    def check_form(form: LessonCreateForm):
        """Добавление урока с историей операций"""
        if not form.is_valid():
            return JsonResponse(
                {"status": "error", "errors": form.errors},
                status=400
            )

    @staticmethod
    def create_lesson(data: dict) -> dict:
        """
        Application layer:
        - получает уже валидированные данные
        - управляет бизнес-логикой
        """

        lesson = Lesson.objects.create(**data)

        lesson_data = {
            'id': lesson.id,
            'title': lesson.title,
            'start_time': lesson.start_time,
            'description': getattr(lesson, 'description', ''),
            'duration': getattr(lesson, 'duration', 60),
            'created_at': datetime.now().isoformat(),
        }

        return lesson_data

    @staticmethod
    def add_new_task(lesson_data: dict):
        reminder_task = external_celery.send_task(
            'lesson.schedule_reminder',
            args=[lesson_data]
        )
        print(f"✅ Задача напоминания запланирована: {reminder_task.id}")

    @staticmethod
    def send_websocket_message(message: str):
        """
        Отправляет простое текстовое сообщение всем подключенным клиентам

        Args:
            message: Текст сообщения (простая строка)
        """
        try:
            # Получаем channel layer
            channel_layer = get_channel_layer()

            # Отправляем сообщение в группу "notifications"
            async_to_sync(channel_layer.group_send)(
                "notifications",
                {
                    'type': 'send_simple_message',
                    'message': message
                }
            )
            print(f"✅ Сообщение отправлено в WebSocket: {message}")

        except Exception as e:
            print(f"❌ Ошибка отправки WebSocket: {e}")


lesson_domain = LessonDomain()
