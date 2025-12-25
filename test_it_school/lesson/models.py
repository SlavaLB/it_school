from django.utils import timezone
from django.core.exceptions import ValidationError

from django.db import models


class Lesson(models.Model):
    """Модель урока"""

    STATUS_CHOICES = [
        ('scheduled', 'Запланирован'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    title = models.CharField(verbose_name="Название урока",
                             max_length=200,
                             help_text="Например: 'Введение в Python'"
                             )
    description = models.TextField(verbose_name="Описание",
                                   blank=True,
                                   help_text="Детальное описание урока"
                                   )
    start_time = models.DateTimeField(verbose_name="Время начала урока")
    end_time = models.DateTimeField(verbose_name="Время окончания урока",
                                    blank=True,
                                    null=True
                                    )
    status = models.CharField(verbose_name="Статус урока",
                              max_length=20,
                              choices=STATUS_CHOICES,
                              default='scheduled'
                              )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    completed_at = models.DateTimeField(null=True,
                                        blank=True,
                                        verbose_name="Дата завершения"
                                        )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_time'])
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_time__lt=models.F('end_time')),
                name="lesson_end_after_start"
            )
        ]

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        """Автоматически устанавливаем end_time, если не задан"""

        if not self.end_time and self.start_time:
            # По умолчанию: урок длится 45 минут
            self.end_time = self.start_time + timezone.timedelta(minutes=45)

        # Если завершаем урок, ставим время завершения
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

    def clean(self):
        """Валидация данных"""
        errors = {}

        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                errors['end_time'] = 'Время окончания должно быть позже времени начала'

        if self.start_time and self.start_time < timezone.now():
            errors['start_time'] = 'Нельзя создать урок в прошлом'

        if errors:
            raise ValidationError(errors)
