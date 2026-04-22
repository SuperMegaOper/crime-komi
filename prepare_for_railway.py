import os
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()

# Правильное содержимое start.sh
CORRECT_START_SH = """#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_superuser_if_none
gunicorn crime_komi.wsgi
"""

# 1. Полностью удаляем старый start.sh и все его резервные копии
start_path = PROJECT_DIR / "start.sh"
if start_path.exists():
    os.remove(start_path)
    print("🗑️ Удалён старый start.sh")
for bak in PROJECT_DIR.glob("start.sh*"):
    if bak.name != "start.sh":
        os.remove(bak)
        print(f"🗑️ Удалён {bak.name}")

# 2. Создаём новый start.sh с правильным содержимым
with open(start_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(CORRECT_START_SH)
print("✅ Создан новый start.sh")

# 3. Удаляем все временные скрипты, которые могли содержать конфликты
temp_scripts = [
    "prepare_for_railway_final.py",
    "fix_start_sh_conflict.py",
    "apply_mobile_fixes.py",
    "fix_all_and_push.py",
    "final_fix_and_push.py",
    "fix_all_conflicts_and_errors.py",
    "emergency_fix_start_sh.py",  # удалит сам себя после выполнения
]
for script in temp_scripts:
    script_path = PROJECT_DIR / script
    if script_path.exists():
        os.remove(script_path)
        print(f"🗑️ Удалён {script}")

# 4. Проверяем, что в settings.py нет конфликтов
settings_path = PROJECT_DIR / "crime_komi" / "settings.py"
if settings_path.exists():
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "<<<<<<< HEAD" in content:
        # Удаляем маркеры конфликта
        lines = content.splitlines()
        new_lines = []
        skip = False
        for line in lines:
            if line.startswith("<<<<<<< HEAD"):
                skip = True
                continue
            if skip and line.startswith("======="):
                skip = False
                continue
            if not skip and not line.startswith(">>>>>>>"):
                new_lines.append(line)
        clean_content = "\n".join(new_lines)
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
        print("✅ Исправлены конфликты в settings.py")

# 5. Закоммитить и запушить
import subprocess
def run(cmd):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, cwd=PROJECT_DIR)

run("git add .")
run('git commit -m "Emergency fix: correct start.sh, remove conflicts"')
run("git push origin main")

print("\n✅ Готово! Теперь перезапустите деплой на Railway.")