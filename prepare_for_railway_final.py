import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
APP_NAME = "incidents"
MANAGEMENT_DIR = PROJECT_DIR / APP_NAME / "management"
COMMANDS_DIR = MANAGEMENT_DIR / "commands"
SETTINGS_FILE = PROJECT_DIR / "crime_komi" / "settings.py"
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
START_SH_FILE = PROJECT_DIR / "start.sh"
GITIGNORE_FILE = PROJECT_DIR / ".gitignore"

def backup_file(path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".railwayprep")
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

print("🚀 Начинаем финальную подготовку проекта для Railway...")

# 1. Создаём структуру management/commands
COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
(COMMANDS_DIR.parent / "__init__.py").touch(exist_ok=True)
(COMMANDS_DIR / "__init__.py").touch(exist_ok=True)

# 2. Создаём файл команды create_superuser_if_none.py
command_content = '''from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Создаёт суперпользователя, если он не существует'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'defaultpassword')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Суперпользователь "{username}" успешно создан!'))
        else:
            self.stdout.write(self.style.WARNING(f'Суперпользователь "{username}" уже существует.'))
'''
command_file = COMMANDS_DIR / "create_superuser_if_none.py"
with open(command_file, "w", encoding="utf-8") as f:
    f.write(command_content)
print("✅ Создан файл команды: incidents/management/commands/create_superuser_if_none.py")

# 3. Создаём или обновляем start.sh
start_content = '''#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_superuser_if_none
gunicorn crime_komi.wsgi
'''
if START_SH_FILE.exists():
    with open(START_SH_FILE, "r") as f:
        existing = f.read()
    if "create_superuser_if_none" not in existing:
        backup_file(START_SH_FILE)
        # Добавляем команду перед gunicorn
        lines = existing.splitlines()
        new_lines = []
        for line in lines:
            if "gunicorn" in line and "create_superuser_if_none" not in "\n".join(new_lines):
                new_lines.append("python manage.py create_superuser_if_none")
            new_lines.append(line)
        with open(START_SH_FILE, "w") as f:
            f.write("\n".join(new_lines))
        print("✅ Обновлён start.sh (добавлена команда create_superuser_if_none)")
    else:
        print("✅ start.sh уже содержит команду create_superuser_if_none")
else:
    with open(START_SH_FILE, "w") as f:
        f.write(start_content)
    print("✅ Создан start.sh")

# 4. Добавляем dj-database-url в requirements.txt
if REQUIREMENTS_FILE.exists():
    with open(REQUIREMENTS_FILE, "r") as f:
        req = f.read()
    if "dj-database-url" not in req:
        backup_file(REQUIREMENTS_FILE)
        with open(REQUIREMENTS_FILE, "a") as f:
            f.write("\ndj-database-url==2.2.0\n")
        print("✅ Добавлен dj-database-url в requirements.txt")
    else:
        print("✅ dj-database-url уже есть в requirements.txt")
else:
    print("⚠️ requirements.txt не найден, создаём...")
    with open(REQUIREMENTS_FILE, "w") as f:
        f.write("dj-database-url==2.2.0\n")
    print("✅ Создан requirements.txt с dj-database-url")

# 5. Обновляем settings.py
if SETTINGS_FILE.exists():
    backup_file(SETTINGS_FILE)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    # Добавляем import dj_database_url
    if "import dj_database_url" not in content:
        content = content.replace("import os\n", "import os\nimport dj_database_url\n")
    # Заменяем DATABASES на dj_database_url.config
    if "dj_database_url.config" not in content:
        import re
        pattern = r"DATABASES\s*=\s*\{[^}]+\}"
        new_db = "DATABASES = {\n    'default': dj_database_url.config(\n        default='sqlite:///db.sqlite3',\n        conn_max_age=600,\n        conn_health_checks=True,\n    )\n}"
        content = re.sub(pattern, new_db, content, flags=re.DOTALL)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Обновлён settings.py (DATABASES через dj_database_url)")
    else:
        print("✅ settings.py уже настроен")
else:
    print("❌ settings.py не найден")

# 6. Обновляем .gitignore
if GITIGNORE_FILE.exists():
    with open(GITIGNORE_FILE, "r") as f:
        gitignore = f.read()
    if "staticfiles/" not in gitignore:
        with open(GITIGNORE_FILE, "a") as f:
            f.write("\nstaticfiles/\n")
        print("✅ Добавлена папка staticfiles/ в .gitignore")
    else:
        print("✅ .gitignore уже содержит staticfiles/")
else:
    print("⚠️ .gitignore не найден, создаём...")
    with open(GITIGNORE_FILE, "w") as f:
        f.write("venv/\n__pycache__/\n*.pyc\n*.log\n.env\nstaticfiles/\nmedia/\ndb.sqlite3\n")
    print("✅ Создан .gitignore")

# 7. Обновляем .env.example
env_example = '''# Переменные окружения для Railway
# База данных (автоматически добавляется при создании PostgreSQL)
DATABASE_URL=postgresql://...

# Суперпользователь (создаётся автоматически при запуске)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=very_secret_password

# Секретный ключ Django (сгенерируйте новый)
SECRET_KEY=django-insecure-your-secret-key-here
'''
env_example_path = PROJECT_DIR / ".env.example"
with open(env_example_path, "w") as f:
    f.write(env_example)
print("✅ Обновлён .env.example с примерами переменных")

# 8. Коммит и пуш в GitHub
print("\n📦 Отправка изменений в GitHub...")
run_cmd("git add .")
run_cmd('git commit -m "Final Railway preparation: superuser auto-creation, start.sh, dj-database-url, settings update"')
run_cmd("git push origin main")

print("\n🎉 Скрипт завершён! Теперь сделайте следующее:")
print("1. На Railway перейдите в ваш проект → веб-сервис → вкладка Variables.")
print("2. Добавьте переменные окружения:")
print("   - DJANGO_SUPERUSER_USERNAME (например, admin)")
print("   - DJANGO_SUPERUSER_EMAIL (ваш email)")
print("   - DJANGO_SUPERUSER_PASSWORD (надёжный пароль)")
print("   - SECRET_KEY (сгенерируйте: https://djecrety.ir/ или командой python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')")
print("3. Убедитесь, что переменная DATABASE_URL присутствует (должна появиться после создания базы данных). Если нет, добавьте её через Reference → выберите вашу базу PostgreSQL → DATABASE_URL.")
print("4. Перезапустите деплой: Deploy → Deploy Now.")
print("5. После деплоя суперпользователь создастся автоматически, и вы сможете войти в админку.")