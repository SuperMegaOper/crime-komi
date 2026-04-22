import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
MODELS_PATH = PROJECT_DIR / "incidents" / "models.py"

# Бэкап текущего файла
if MODELS_PATH.exists():
    shutil.copy2(MODELS_PATH, MODELS_PATH.with_suffix(".py.badbackup"))
    print("Создан бэкап повреждённого models.py (.badbackup)")

# Корректное содержимое
correct_content = '''from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Incident(models.Model):
    CATEGORY_CHOICES = [
        ('кража', 'Кража'),
        ('грабеж', 'Грабеж'),
        ('разбой', 'Разбой'),
        ('убийство', 'Убийство'),
        ('мошенничество', 'Мошенничество'),
        ('хулиганство', 'Хулиганство'),
        ('другое', 'Другое'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('confirmed', 'Подтверждено'),
        ('rejected', 'Отклонено'),
    ]
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    latitude = models.FloatField(verbose_name='Широта')
    longitude = models.FloatField(verbose_name='Долгота')
    date_occurred = models.DateField(verbose_name='Дата происшествия')
    place = models.CharField(max_length=300, blank=True, verbose_name='Адрес места')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Добавил пользователь')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Происшествие"
        verbose_name_plural = "Происшествия"

    def __str__(self):
        return f"{self.title} - {self.category}"

class AnonymousReport(models.Model):
    subject = models.CharField(max_length=200, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    location = models.CharField(max_length=300, blank=True, verbose_name="Место (необязательно)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Анонимное обращение"
        verbose_name_plural = "Анонимные обращения"

    def __str__(self):
        return f"Обращение от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    avatar = models.CharField(max_length=500, blank=True, null=True, verbose_name="Аватар (URL)")
    bio = models.TextField(blank=True, verbose_name="О себе")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Профиль {self.user.username}"
    
    def get_incident_count(self):
        return self.user.incident_set.filter(status='confirmed').count()

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
'''

# Записываем исправленный файл
with open(MODELS_PATH, "w", encoding="utf-8") as f:
    f.write(correct_content)

print("✅ Файл models.py полностью перезаписан корректной версией (с русскими verbose_name и без ошибок).")
print("\nТеперь выполните последовательно:")
print("python manage.py makemigrations incidents")
print("python manage.py migrate")
print("python manage.py runserver")