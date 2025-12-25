from django.urls import path
from .views import main, lesson_add, lesson_list

app_name = "lesson"

urlpatterns = [
    path('', main, name="main"),
    path('lesson_add/', lesson_add, name="lesson_add"),
    path('lessons/', lesson_list, name="lesson_list"),
]
