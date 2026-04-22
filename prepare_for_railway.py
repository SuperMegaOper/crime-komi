import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
SETTINGS_FILE = PROJECT_DIR / "crime_komi" / "settings.py"
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
PROCFILE = PROJECT_DIR / "Procfile"
RUNTIME_TXT = PROJECT_DIR / "runtime.txt"

def run_cmd(cmd, cwd=None):
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        print(f"⚠️ Команда завершилась с ошибкой (код {result.returncode})")
    else:
        print(result.stdout)
    return result

def backup_file(path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".railwaybak")
        import shutil
        shutil.copy2(path, bak)
        print(f"Резервная копия: {bak.name}")

print("🚀 Начинаем подготовку проекта к деплою на Railway...\n")

# 1. Установка необходимых пакетов
print("📦 Установка gunicorn, whitenoise, psycopg2-binary...")
run_cmd("pip install gunicorn whitenoise psycopg2-binary")

print("\n📄 Обновление requirements.txt...")
run_cmd("pip freeze > requirements.txt")

# 2. Настройка settings.py
if SETTINGS_FILE.exists():
    backup_file(SETTINGS_FILE)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Добавляем import os и dj_database_url, если нет
    if "import os" not in content:
        content = "import os\n" + content
    if "import dj_database_url" not in content:
        content = content.replace("import os\n", "import os\nimport dj_database_url\n")
    
    # Добавляем WhiteNoise в MIDDLEWARE
    if "whitenoise.middleware.WhiteNoiseMiddleware" not in content:
        content = content.replace(
            "MIDDLEWARE = [",
            "MIDDLEWARE = [\n    'whitenoise.middleware.WhiteNoiseMiddleware',"
        )
        # Убедимся, что WhiteNoise идёт сразу после SecurityMiddleware
        content = re.sub(
            r"('django\.middleware\.security\.SecurityMiddleware',)\s*('whitenoise\.middleware\.WhiteNoiseMiddleware',)",
            r"\1\n    \2",
            content
        )
    
    # Заменяем DATABASES на конфигурацию через dj_database_url
    db_pattern = r"DATABASES = \{\s*'default':\s*\{[^}]+\}\s\}"
    new_db = "DATABASES = {\n    'default': dj_database_url.config(\n        default='sqlite:///db.sqlite3',\n        conn_max_age=600,\n        conn_health_checks=True,\n    )\n}"
    if re.search(db_pattern, content, re.DOTALL):
        content = re.sub(db_pattern, new_db, content, flags=re.DOTALL)
    else:
        # Если не нашли стандартный блок, добавим в конец
        content += "\n\n" + new_db
    
    # Добавляем настройки статики для WhiteNoise
    if "STATICFILES_STORAGE" not in content:
        content += "\n# WhiteNoise static files storage\nSTATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'\n"
    if "STATIC_ROOT" not in content:
        content += "STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')\n"
    
    # Устанавливаем ALLOWED_HOSTS на время деплоя (можно потом изменить)
    if "ALLOWED_HOSTS" in content:
        content = re.sub(r"ALLOWED_HOSTS\s*=\s*\[.*?\]", "ALLOWED_HOSTS = ['*']", content, flags=re.DOTALL)
    else:
        content += "\nALLOWED_HOSTS = ['*']\n"
    
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ settings.py обновлён (WhiteNoise, DATABASES через dj-database-url, ALLOWED_HOSTS, статика).")
else:
    print("❌ settings.py не найден!")
    sys.exit(1)

# 3. Создаём Procfile
PROCFILE_CONTENT = "web: gunicorn crime_komi.wsgi --log-file -\n"
with open(PROCFILE, "w", encoding="utf-8") as f:
    f.write(PROCFILE_CONTENT)
print(f"✅ Создан {PROCFILE.name}")

# 4. Определяем версию Python и создаём runtime.txt
python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
# Получаем точную версию
try:
    result = subprocess.run("python --version", shell=True, capture_output=True, text=True)
    version_str = result.stdout.strip().split()[1]  # "Python 3.12.4" -> "3.12.4"
    major_minor = '.'.join(version_str.split('.')[:2])  # "3.12"
    runtime_version = f"python-{version_str}"  # "python-3.12.4"
except:
    runtime_version = f"python-{python_version}.0"
with open(RUNTIME_TXT, "w", encoding="utf-8") as f:
    f.write(runtime_version + "\n")
print(f"✅ Создан {RUNTIME_TXT.name} с версией {runtime_version}")

# 5. Проверяем, есть ли .gitignore, и добавляем туда venv, __pycache__, .env и т.д.
gitignore = PROJECT_DIR / ".gitignore"
if not gitignore.exists():
    gitignore_content = """venv/
__pycache__/
*.pyc
*.log
.env
staticfiles/
media/
db.sqlite3
.DS_Store
"""
    with open(gitignore, "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("✅ Создан .gitignore")
else:
    print("⚠️ .gitignore уже существует, проверьте наличие venv, __pycache__, .env в нём.")

# 6. Git commit и push
print("\n📦 Отправка изменений в GitHub...")
# Проверяем, есть ли git репозиторий
if not (PROJECT_DIR / ".git").exists():
    print("Инициализируем git репозиторий...")
    run_cmd("git init")
    run_cmd("git add .")
    run_cmd('git commit -m "Initial commit"')
else:
    run_cmd("git add .")
    run_cmd('git commit -m "Prepare for Railway deployment (add gunicorn, whitenoise, settings update)"')

# Проверяем удалённый репозиторий
remote_check = run_cmd("git remote -v")
if "origin" not in remote_check.stdout:
    print("\n⚠️ Удалённый репозиторий не настроен.")
    repo_url = input("Введите URL вашего GitHub репозитория (например, https://github.com/ваш_логин/crime-komi.git): ").strip()
    if repo_url:
        run_cmd(f"git remote add origin {repo_url}")
        run_cmd("git branch -M main")
        run_cmd("git push -u origin main")
    else:
        print("Пропускаем push. Выполните git push вручную.")
else:
    run_cmd("git push -u origin main")

print("\n🎉 Подготовка завершена! Теперь идите на railway.app и создайте новый проект из этого репозитория.")