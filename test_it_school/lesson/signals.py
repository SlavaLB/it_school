from django.db.models.signals import post_migrate
from django.contrib.auth.models import User
from django.dispatch import receiver


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    """Создает суперпользователя после миграций"""
    # Проверяем, что это наше приложение
    if sender.name == 'lesson':
        # Проверяем, не существует ли уже суперпользователь
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("✅ Суперпользователь создан: admin / admin123")
