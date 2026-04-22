import os
import re
import subprocess
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
SETTINGS_FILE = PROJECT_DIR / "crime_komi" / "settings.py"
BASE_HTML = PROJECT_DIR / "incidents" / "templates" / "incidents" / "base.html"
CSS_PATH = PROJECT_DIR / "incidents" / "static" / "incidents" / "css" / "style.css"

def run_cmd(cmd, cwd=None):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        return False
    else:
        print(result.stdout)
        return True

def backup_file(path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".finalfix")
        shutil.copy2(path, bak)
        print(f"📁 Резервная копия: {bak.name}")

# ------------------------- 1. Решаем конфликт git -------------------------
print("\n🔧 1. Разрешаем конфликты Git (pull --rebase)...")
run_cmd("git fetch origin")
run_cmd("git rebase origin/main")
# Если конфликт остался, предложим вручную
if (PROJECT_DIR / ".git" / "rebase-merge").exists() or (PROJECT_DIR / ".git" / "rebase-apply").exists():
    print("\n⚠️ Обнаружен конфликт при rebase. Открывайте файлы и исправляйте.")
    print("После исправления выполните: git add . && git rebase --continue")
    input("Нажмите Enter, когда конфликты будут разрешены...")

# ------------------------- 2. Обновляем settings.py (CSRF) -------------------------
if SETTINGS_FILE.exists():
    backup_file(SETTINGS_FILE)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    railway_domain = "crime-komi-production.up.railway.app"
    # ALLOWED_HOSTS
    if "ALLOWED_HOSTS" in content:
        content = re.sub(r"ALLOWED_HOSTS\s*=\s*\[.*?\]", f"ALLOWED_HOSTS = ['{railway_domain}', 'localhost', '127.0.0.1']", content, flags=re.DOTALL)
    else:
        content += f"\nALLOWED_HOSTS = ['{railway_domain}', 'localhost', '127.0.0.1']\n"
    # CSRF_TRUSTED_ORIGINS
    if "CSRF_TRUSTED_ORIGINS" in content:
        content = re.sub(r"CSRF_TRUSTED_ORIGINS\s*=\s*\[.*?\]", f"CSRF_TRUSTED_ORIGINS = ['https://{railway_domain}']", content, flags=re.DOTALL)
    else:
        content += f"\nCSRF_TRUSTED_ORIGINS = ['https://{railway_domain}']\n"
    # Дополнительные настройки безопасности для Railway
    if "SECURE_PROXY_SSL_HEADER" not in content:
        content += "\nSECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')\nUSE_X_FORWARDED_HOST = True\n"
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ settings.py обновлён (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, SSL).")
else:
    print("❌ settings.py не найден")

# ------------------------- 3. Мобильная адаптация карты (кнопка) -------------------------
if CSS_PATH.exists():
    backup_file(CSS_PATH)
    with open(CSS_PATH, "a", encoding="utf-8") as f:
        f.write("""
/* Мобильная версия: карта скрыта, появляется по кнопке */
@media (max-width: 768px) {
    .map-container {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1050;
        background: rgba(0,0,0,0.9);
    }
    .map-container.active {
        display: block;
    }
    #map {
        height: 90%;
        margin-top: 10px;
    }
    .close-map-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 1060;
        background: #c0392b;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 5px 12px;
        cursor: pointer;
    }
    .show-map-btn {
        display: block;
        width: 100%;
        background: #c0392b;
        color: white;
        border: none;
        border-radius: 40px;
        padding: 10px;
        margin-top: 10px;
        font-size: 1rem;
        cursor: pointer;
    }
}
@media (min-width: 769px) {
    .show-map-btn {
        display: none;
    }
    .close-map-btn {
        display: none;
    }
    .map-container {
        display: block !important;
    }
}
""")
    print("✅ Добавлены стили для мобильной карты (скрыта, открывается по кнопке)")

if BASE_HTML.exists():
    backup_file(BASE_HTML)
    with open(BASE_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    # Добавляем кнопку перед map-container
    if '<div class="map-container">' in content and 'show-map-btn' not in content:
        button_html = '<button class="show-map-btn" id="showMapBtn">📱 Показать карту</button>\n'
        close_button = '<button class="close-map-btn" id="closeMapBtn">✕ Закрыть</button>\n'
        content = content.replace('<div class="map-container">', button_html + '<div class="map-container">')
        content = content.replace('<div id="map"></div>', close_button + '<div id="map"></div>')
        # Добавляем скрипт
        js_script = """
<script>
    (function() {
        var mapContainer = document.querySelector('.map-container');
        var showBtn = document.getElementById('showMapBtn');
        var closeBtn = document.getElementById('closeMapBtn');
        if (showBtn) {
            showBtn.addEventListener('click', function() {
                mapContainer.classList.add('active');
                if (window.map) { setTimeout(function() { window.map.invalidateSize(); }, 100); }
            });
        }
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                mapContainer.classList.remove('active');
            });
        }
    })();
</script>
"""
        content = content.replace('</body>', js_script + '\n</body>')
        with open(BASE_HTML, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ base.html обновлён (добавлена кнопка показа карты)")
    else:
        print("⚠️ base.html уже содержит кнопку или не найден блок map-container")
else:
    print("❌ base.html не найден")

# ------------------------- 4. Коммит и push -------------------------
print("\n📦 4. Сохраняем изменения и отправляем в GitHub...")
run_cmd("git add .")
run_cmd('git commit -m "Fix CSRF, mobile map toggle, and settings for Railway"')
run_cmd("git push --force-with-lease origin main")

print("\n🎉 Скрипт завершён! Теперь:")
print("1. Перейдите на Railway → ваш сервис 'crime-komi' → вкладка Deployments.")
print("2. Нажмите на последний деплой → кнопку 'Redeploy'.")
print("3. После перезапуска проверьте работу входа и мобильной карты.")
print("4. Если вход всё ещё не работает, добавьте вручную в Variables: CSRF_TRUSTED_ORIGINS = https://crime-komi-production.up.railway.app (но это уже должно быть в коде).")