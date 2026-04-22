import os
import re
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
APP_NAME = "incidents"
VIEWS_PATH = PROJECT_DIR / APP_NAME / "views.py"
MODELS_PATH = PROJECT_DIR / APP_NAME / "models.py"

def backup_file(path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".regfix")
        shutil.copy2(path, bak)
        print(f"📁 Резервная копия: {bak.name}")

# 1. Добавляем метод get_incident_count в модель Profile, если его нет
if MODELS_PATH.exists():
    backup_file(MODELS_PATH)
    with open(MODELS_PATH, "r", encoding="utf-8") as f:
        models_content = f.read()
    
    if "def get_incident_count" not in models_content:
        # Находим класс Profile и добавляем метод
        method_code = """
    def get_incident_count(self):
        return self.user.incident_set.filter(status='confirmed').count()
"""
        # Вставляем после поля bio или в конец класса
        if "class Profile" in models_content:
            # Ищем конец класса (строка с return или отступ)
            lines = models_content.split('\n')
            in_profile = False
            indent = None
            for i, line in enumerate(lines):
                if 'class Profile' in line:
                    in_profile = True
                    continue
                if in_profile and line.strip() and not line.startswith(' '):
                    # Конец класса
                    lines.insert(i, method_code)
                    break
                if in_profile and 'def __str__' in line:
                    lines.insert(i, method_code)
                    break
            else:
                # Если не нашли, добавим в конец файла перед последним return?
                models_content += method_code
            models_content = '\n'.join(lines)
            with open(MODELS_PATH, "w", encoding="utf-8") as f:
                f.write(models_content)
            print("✅ Добавлен метод get_incident_count в модель Profile")
        else:
            print("⚠️ Класс Profile не найден в models.py")
    else:
        print("✅ Метод get_incident_count уже есть в Profile")
else:
    print("❌ models.py не найден")

# 2. Убеждаемся, что ajax_register корректно создаёт пользователя и профиль
if VIEWS_PATH.exists():
    backup_file(VIEWS_PATH)
    with open(VIEWS_PATH, "r", encoding="utf-8") as f:
        views_content = f.read()
    
    # Проверяем наличие функции ajax_register
    if "def ajax_register" not in views_content:
        # Добавляем функцию
        ajax_register_func = """
def ajax_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            return JsonResponse({'success': False, 'error': 'Пароли не совпадают.'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Имя пользователя уже занято.'})
        user = User.objects.create_user(username=username, email=email, password=password)
        # Профиль создастся автоматически через сигнал, но на всякий случай:
        Profile.objects.get_or_create(user=user)
        login(request, user)
        return JsonResponse({'success': True, 'username': user.username})
    return JsonResponse({'success': False, 'error': 'Метод не разрешён.'})
"""
        views_content += ajax_register_func
        print("✅ Добавлена функция ajax_register в views.py")
    else:
        # Обновляем существующую, добавив создание профиля и исправив импорты
        if 'Profile.objects.get_or_create' not in views_content:
            views_content = views_content.replace(
                "user = User.objects.create_user(username=username, email=email, password=password)",
                "user = User.objects.create_user(username=username, email=email, password=password)\n        Profile.objects.get_or_create(user=user)"
            )
            print("✅ Обновлена ajax_register: добавлено создание профиля")
    
    # Убедимся, что есть импорт Profile
    if "from .models import Profile" not in views_content:
        # Добавим после других импортов
        lines = views_content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("from .models") or line.startswith("from incidents.models"):
                insert_pos = i + 1
        lines.insert(insert_pos, "from .models import Profile")
        views_content = '\n'.join(lines)
        print("✅ Добавлен импорт Profile в views.py")
    
    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(views_content)
else:
    print("❌ views.py не найден")

# 3. Проверяем наличие URL для ajax_register
urls_path = PROJECT_DIR / APP_NAME / "urls.py"
if urls_path.exists():
    with open(urls_path, "r", encoding="utf-8") as f:
        urls_content = f.read()
    if "ajax_register" not in urls_content:
        # Добавляем маршрут
        urls_content = urls_content.replace("urlpatterns = [", 
            "urlpatterns = [\n    path('ajax/register/', views.ajax_register, name='ajax_register'),")
        with open(urls_path, "w", encoding="utf-8") as f:
            f.write(urls_content)
        print("✅ Добавлен URL для ajax_register")
    else:
        print("✅ URL для ajax_register уже существует")

print("\n🎉 Регистрация пользователей теперь должна работать.")
print("Перезапустите сервер: python manage.py runserver")