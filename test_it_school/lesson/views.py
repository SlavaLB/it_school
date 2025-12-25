from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from lesson.aplication import lesson_app
from lesson.models import Lesson


async def main(request):
    return render(request, 'main.html')


@require_POST
def lesson_add(request):
    """
        Обработчик HTTP-запроса для создания нового урока.

        Этот view является точкой входа для создания урока. Он делегирует
        выполнение бизнес-логики классу LessonApplication, который управляет
        всей последовательностью операций и ведет их историю.

        Parameters:
            request (HttpRequest): HTTP-запрос с данными формы урока

        Returns:
            JsonResponse: JSON ответ с результатом операции:
                - status: 'ok' при успехе
                - lesson_id: ID созданного урока (при успехе)
                - errors: ошибки валидации (при ошибке)

        Status Codes:
            201: Урок успешно создан
            400: Ошибка валидации данных
            401: Требуется авторизация
            500: Внутренняя ошибка сервера

        Example:
            POST /lesson_add/
            Content-Type: application/x-www-form-urlencoded

            title=Математика&start_time=2025-12-25+10:00:00&duration=60
    """
    # История операций
    try:

        lesson_app.lesson_add(request=request)
        return JsonResponse(
            {"status": "ok"},
            status=201
        )
    except Exception as e:
        return JsonResponse(
            {
                "status": f"Непредвиденная ошибка в lesson_add: {str(e)}",
                "message": "Внутренняя ошибка сервера при создании урока"
            },
            status=500
        )


@require_GET
def lesson_list(request):
    # Пример плохого эндпоинта
    page_number = request.GET.get("page", 1)

    qs = Lesson.objects.order_by("-start_time")

    paginator = Paginator(qs, 3)
    page = paginator.get_page(page_number)

    lessons = [
        {
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "start_time": lesson.start_time.isoformat(),
            "end_time": lesson.end_time.isoformat() if lesson.end_time else None,
            "status": lesson.status,
        }
        for lesson in page.object_list
    ]
    return JsonResponse(
        {
            "items": lessons,
            "pagination": {
                "page": page.number,
                "pages": paginator.num_pages,
                "has_next": page.has_next(),
                "has_prev": page.has_previous(),
            }
        }
    )
