import os
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()

def run_cmd(cmd, cwd=None):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        return False
    else:
        print(result.stdout)
        return True

# 1. Удаляем мусорные файлы, которые не должны быть в репозитории
print("🧹 Удаляем временные файлы...")
for f in ["start.sh.bad", "start.sh.conflictfix", "prepare_for_railway_final.py"]:
    file_path = PROJECT_DIR / f
    if file_path.exists():
        os.remove(file_path)
        print(f"🗑️ Удалён {f}")

# 2. Сначала забираем изменения с GitHub
print("\n📥 Получаем изменения с GitHub...")
run_cmd("git fetch origin")
run_cmd("git rebase origin/main")

# Если конфликт всё же возник, предложим ручное разрешение
if (PROJECT_DIR / ".git" / "rebase-merge").exists() or (PROJECT_DIR / ".git" / "rebase-apply").exists():
    print("\n⚠️ Обнаружен конфликт при rebase. Нужно вручную разрешить конфликты в файлах.")
    print("После разрешения конфликтов выполните:")
    print("  git add .")
    print("  git rebase --continue")
    print("Затем запустите этот скрипт снова.")
    exit(1)

# 3. Проверяем, что start.sh правильный
start_sh = PROJECT_DIR / "start.sh"
correct_start = """#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_superuser_if_none
gunicorn crime_komi.wsgi
"""
if start_sh.exists():
    with open(start_sh, "r", encoding="utf-8") as f:
        current = f.read()
    if current != correct_start:
        with open(start_sh, "w", encoding="utf-8", newline="\n") as f:
            f.write(correct_start)
        print("✅ Исправлен start.sh")
else:
    with open(start_sh, "w", encoding="utf-8", newline="\n") as f:
        f.write(correct_start)
    print("✅ Создан start.sh")

# 4. Добавляем недостающие настройки в settings.py
settings_path = PROJECT_DIR / "crime_komi" / "settings.py"
if settings_path.exists():
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = f.read()
    railway_domain = "crime-komi-production.up.railway.app"
    if "CSRF_TRUSTED_ORIGINS" not in settings:
        settings += f"\nCSRF_TRUSTED_ORIGINS = ['https://{railway_domain}']\n"
    if "SECURE_PROXY_SSL_HEADER" not in settings:
        settings += "\nSECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')\nUSE_X_FORWARDED_HOST = True\n"
    # Убедимся, что ALLOWED_HOSTS содержит домен
    import re
    if "ALLOWED_HOSTS" in settings:
        settings = re.sub(r"ALLOWED_HOSTS\s*=\s*\[.*?\]", f"ALLOWED_HOSTS = ['{railway_domain}', 'localhost', '127.0.0.1']", settings, flags=re.DOTALL)
    else:
        settings += f"\nALLOWED_HOSTS = ['{railway_domain}', 'localhost', '127.0.0.1']\n"
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(settings)
    print("✅ settings.py обновлён")

# 5. Коммитим все изменения
run_cmd("git add .")
run_cmd('git commit -m "Fix start.sh, settings, remove temp files"')

# 6. Отправляем на GitHub (безопасный push)
run_cmd("git push origin main")

print("\n🎉 Готово! Теперь:")
print("1. Перезапустите деплой на Railway (Deployments → Redeploy).")
print("2. Мобильная версия карты будет работать (по кнопке).")
print("3. CSRF должен быть исправлен.")