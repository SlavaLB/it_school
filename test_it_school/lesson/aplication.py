from lesson.domain import LessonDomain
from lesson.forms import LessonCreateForm


class LessonApplication:
    """
    Прикладной сервис для управления операциями с уроками.

    Отвечает за координацию последовательности действий при работе с уроками,
    ведение истории операций и обеспечение целостности бизнес-процессов.

    Attributes:
        lesson_domain (LessonDomain): Экземпляр доменного сервиса для
            выполнения бизнес-логики
        operation_history (list): История выполненных операций в рамках
            текущей сессии

    Note:
        Каждый публичный метод этого класса представляет собой законченный
        бизнес-сценарий (use case).
    """

    def __init__(self, lesson_domain: LessonDomain = None):
        self.lesson_domain = lesson_domain

    def lesson_add(self, request):
        """Добавление урока с историей операций"""

        # 1 Получение данных из формы
        form = LessonCreateForm(request.POST)

        # 2 Валидация формы
        self.lesson_domain.check_form(form)

        # 3 Создание объекта Lesson
        # Возврат объекта в виде словаря
        lesson = self.lesson_domain.create_lesson(data=form.cleaned_data)

        # 4 Постановка задачи в Celery
        self.lesson_domain.add_new_task(lesson)

        # 5. Отправка сообщения на клиент
        message = f"Это сообщение по WebSocket получил пользователь который поставил задачу. <br>В Celery уже отправлена задача: <br>Оповестить учеников о том, что у них будет урок - {lesson['title']} <br>Начнется {lesson['start_time'].date()} в {lesson['start_time'].time().strftime("%H:%M")} <br>Также добавлена задача в Celery: <br>Которая предупредит учеников за 5 минут до начала урока <br>Если урок создался менее чем за 5 минут до начала <br>Уведомление придет сразу <br>Посмотреть можно в logs/celery/celery_tasks.log"

        self.lesson_domain.send_websocket_message(message)

        return "Валидация прошла"


lesson_domain_instance = LessonDomain()
lesson_app = LessonApplication(lesson_domain_instance)
