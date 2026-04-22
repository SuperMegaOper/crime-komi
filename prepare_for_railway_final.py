import os
import re
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
SETTINGS_FILE = PROJECT_DIR / "crime_komi" / "settings.py"
START_SH = PROJECT_DIR / "start.sh"

def backup_file(path):
    if path.exists():
        import shutil
        bak = path.with_suffix(path.suffix + ".authfix")
        shutil.copy2(path, bak)
        print(f"Резервная копия: {bak.name}")

def run_cmd(cmd):
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
    else:
        print(result.stdout)
    return result

print("🔧 Исправляем проблемы с авторизацией на Railway...")

# 1. Обновляем settings.py
if SETTINGS_FILE.exists():
    backup_file(SETTINGS_FILE)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Добавляем импорт os, если нет
    if "import os" not in content:
        content = "import os\n" + content

    # Добавляем ALLOWED_HOSTS с поддержкой Railway
    if "ALLOWED_HOSTS" in content:
        # Заменяем существующий ALLOWED_HOSTS
        content = re.sub(
            r"ALLOWED_HOSTS\s*=\s*\[.*?\]",
            "ALLOWED_HOSTS = ['*']",
            content,
            flags=re.DOTALL
        )
    else:
        content += "\nALLOWED_HOSTS = ['*']\n"

    # Добавляем CSRF_TRUSTED_ORIGINS для Railway
    csrf_trusted = '''
# Доверенные источники для CSRF (для Railway)
CSRF_TRUSTED_ORIGINS = [
    'https://*.up.railway.app',
    'http://*.up.railway.app',
    'https://*.railway.app',
]
'''
    if "CSRF_TRUSTED_ORIGINS" not in content:
        content += csrf_trusted
    else:
        content = re.sub(
            r"CSRF_TRUSTED_ORIGINS\s*=\s*\[.*?\]",
            csrf_trusted.strip(),
            content,
            flags=re.DOTALL
        )

    # Добавляем настройки для безопасных сессий (опционально)
    if "SESSION_COOKIE_SECURE" not in content:
        content += "\n# Для HTTPS на Railway\nSESSION_COOKIE_SECURE = True\nCSRF_COOKIE_SECURE = True\nSECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')\n"

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ settings.py обновлён (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, безопасность).")
else:
    print("❌ settings.py не найден")

# 2. Добавляем автоматическое создание суперпользователя в любом случае через сигнал в models.py
models_path = PROJECT_DIR / "incidents" / "models.py"
if models_path.exists():
    backup_file(models_path)
    with open(models_path, "r", encoding="utf-8") as f:
        models_content = f.read()
    # Проверяем, есть ли уже сигнал для создания суперпользователя
    if "create_superuser_if_none" not in models_content:
        # Добавляем функцию в конец файла
        auto_superuser = '''

# Автоматическое создание суперпользователя из переменных окружения (для Railway)
import os
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    if password:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            print(f'✅ Автоматически создан суперпользователь: {username}')
        else:
            print(f'⚠️ Пользователь {username} уже существует')
    else:
        print('⚠️ Не задан пароль суперпользователя (DJANGO_SUPERUSER_PASSWORD)')
'''
        models_content += auto_superuser
        with open(models_path, "w", encoding="utf-8") as f:
            f.write(models_content)
        print("✅ Добавлен автоматический создатель суперпользователя в models.py")
    else:
        print("✅ Автоматическое создание суперпользователя уже есть в models.py")
else:
    print("❌ models.py не найден")

# 3. Обновляем start.sh для вывода отладочной информации
if START_SH.exists():
    backup_file(START_SH)
    with open(START_SH, "r") as f:
        start_content = f.read()
    # Добавляем проверку переменных окружения
    debug_commands = '''
echo "=== Проверка переменных окружения ==="
echo "DJANGO_SUPERUSER_USERNAME: $DJANGO_SUPERUSER_USERNAME"
echo "DJANGO_SUPERUSER_EMAIL: $DJANGO_SUPERUSER_EMAIL"
echo "DJANGO_SUPERUSER_PASSWORD: [скрыто]"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
echo "======================================"
'''
    if "Проверка переменных окружения" not in start_content:
        start_content = start_content.replace("#!/bin/bash", "#!/bin/bash\n\n" + debug_commands)
        with open(START_SH, "w") as f:
            f.write(start_content)
        print("✅ Добавлена отладочная информация в start.sh")
    else:
        print("✅ Отладка уже есть в start.sh")
else:
    print("⚠️ start.sh не найден, создаём...")
    with open(START_SH, "w") as f:
        f.write('''#!/bin/bash
echo "=== Проверка переменных окружения ==="
echo "DJANGO_SUPERUSER_USERNAME: $DJANGO_SUPERUSER_USERNAME"
echo "DJANGO_SUPERUSER_EMAIL: $DJANGO_SUPERUSER_EMAIL"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
echo "======================================"
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_superuser_if_none
gunicorn crime_komi.wsgi
''')
    print("✅ Создан start.sh с отладкой")

# 4. Коммит и пуш
print("\n📦 Отправка изменений в GitHub...")
run_cmd("git add .")
run_cmd('git commit -m "Fix auth: CSRF_TRUSTED_ORIGINS, auto superuser, debug in start.sh"')
run_cmd("git push origin main")

print("\n🎉 Готово! Теперь на Railway:")
print("1. Перезапустите деплой (Deploy → Deploy Now).")
print("2. В логах (Logs) вы увидите отладочную информацию и процесс создания суперпользователя.")
print("3. Обязательно добавьте переменную CSRF_TRUSTED_ORIGINS? Нет, она уже в коде.")
print("4. Проверьте, что в Variables есть:")
print("   - DJANGO_SUPERUSER_USERNAME (ваш логин)")
print("   - DJANGO_SUPERUSER_EMAIL")
print("   - DJANGO_SUPERUSER_PASSWORD (надёжный пароль)")
print("   - SECRET_KEY (сгенерируйте)")
print("   - DATABASE_URL (должна быть автоматически от базы данных)")
print("5. После перезапуска попробуйте войти в админку /admin")
print("6. Регистрация новых пользователей должна работать, так как CSRF_TRUSTED_ORIGINS теперь включает домены Railway.")