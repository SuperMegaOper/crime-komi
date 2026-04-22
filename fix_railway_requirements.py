import os
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
RUNTIME_FILE = PROJECT_DIR / "runtime.txt"

def run_cmd(cmd):
    print(f">>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
    else:
        print(result.stdout)
    return result

# 1. Проверяем, есть ли dj-database-url в requirements.txt
if REQUIREMENTS_FILE.exists():
    with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
        req_text = f.read()
    if "dj-database-url" not in req_text:
        print("➕ Добавляем dj-database-url в requirements.txt")
        with open(REQUIREMENTS_FILE, "a", encoding="utf-8") as f:
            f.write("\ndj-database-url==2.2.0\n")
    else:
        print("✅ dj-database-url уже есть в requirements.txt")
else:
    print("❌ requirements.txt не найден")

# 2. Обновляем runtime.txt на стабильную версию Python 3.12
if RUNTIME_FILE.exists():
    with open(RUNTIME_FILE, "r", encoding="utf-8") as f:
        current = f.read().strip()
    if "3.13" in current:
        print(f"⚠️ Сейчас в runtime.txt: {current}")
        print("Рекомендуется использовать Python 3.12 для совместимости с psycopg2-binary")
        answer = input("Заменить на python-3.12.4? (y/N): ")
        if answer.lower() == "y":
            with open(RUNTIME_FILE, "w", encoding="utf-8") as f:
                f.write("python-3.12.4\n")
            print("✅ runtime.txt обновлён до python-3.12.4")
        else:
            print("Оставлено как есть")
    else:
        print("✅ runtime.txt уже на стабильной версии")
else:
    print("⚠️ runtime.txt не найден, создаём...")
    with open(RUNTIME_FILE, "w", encoding="utf-8") as f:
        f.write("python-3.12.4\n")
    print("✅ Создан runtime.txt с python-3.12.4")

# 3. Закоммитить изменения и запушить
print("\n📦 Отправка изменений в GitHub...")
run_cmd("git add requirements.txt runtime.txt")
run_cmd('git commit -m "Add dj-database-url and fix Python version"')
run_cmd("git push origin main")

print("\n🎉 Готово! После этого перезапустите деплой на Railway.")
print("Убедитесь, что в настройках Railway добавлена переменная DATABASE_URL (привяжите базу данных).")