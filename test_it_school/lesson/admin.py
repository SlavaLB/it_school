from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_time', 'end_time', 'created_at')
    list_filter = ('status', 'start_time')
    search_fields = ('title',)
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description')
        }),
        ('Время проведения', {
            'fields': ('start_time', 'end_time')
        }),
        ('Статус', {
            'fields': ('status', 'completed_at')
        }),
    )
