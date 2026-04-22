import shutil
import subprocess
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
SETTINGS_FILE = PROJECT_DIR / "crime_komi" / "settings.py"
BASE_HTML = PROJECT_DIR / "incidents" / "templates" / "incidents" / "base.html"
CSS_PATH = PROJECT_DIR / "incidents" / "static" / "incidents" / "css" / "style.css"

def backup_file(path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".mobilefix")
        shutil.copy2(path, bak)
        print(f"📁 Резервная копия: {bak.name}")

def run_cmd(cmd):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        return False
    else:
        print(result.stdout)
        return True

# 1. Обновляем CSS (мобильные стили)
if CSS_PATH.exists():
    backup_file(CSS_PATH)
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        css_content = f.read()
    # Проверяем, есть ли уже наши стили
    if ".show-map-btn" not in css_content:
        mobile_css = """
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
    .show-map-btn, .close-map-btn {
        display: none;
    }
    .map-container {
        display: block !important;
    }
}
"""
        with open(CSS_PATH, "a", encoding="utf-8") as f:
            f.write(mobile_css)
        print("✅ Добавлены мобильные стили в style.css")
    else:
        print("⚠️ Мобильные стили уже есть в style.css")
else:
    print("❌ style.css не найден")

# 2. Обновляем base.html (кнопки и скрипт)
if BASE_HTML.exists():
    backup_file(BASE_HTML)
    with open(BASE_HTML, "r", encoding="utf-8") as f:
        html_content = f.read()
    # Добавляем кнопку перед map-container, если её нет
    if "showMapBtn" not in html_content:
        # Вставляем кнопку
        button_html = '<button class="show-map-btn" id="showMapBtn">📱 Показать карту</button>\n'
        if '<div class="map-container">' in html_content:
            html_content = html_content.replace('<div class="map-container">', button_html + '<div class="map-container">')
        # Вставляем кнопку закрытия
        close_button = '<button class="close-map-btn" id="closeMapBtn">✕ Закрыть</button>\n'
        if '<div id="map"></div>' in html_content:
            html_content = html_content.replace('<div id="map"></div>', close_button + '<div id="map"></div>')
        # Добавляем скрипт
        script = '''
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
'''
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', script + '\n</body>')
        with open(BASE_HTML, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✅ base.html обновлён (добавлены кнопки и скрипт)")
    else:
        print("⚠️ base.html уже содержит кнопки")
else:
    print("❌ base.html не найден")

# 3. Обновляем settings.py (CSRF, ALLOWED_HOSTS)
if SETTINGS_FILE.exists():
    backup_file(SETTINGS_FILE)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings_content = f.read()
    railway_domain = "crime-komi-production.up.railway.app"
    # ALLOWED_HOSTS
    if "ALLOWED_HOSTS" in settings_content:
        settings_content = re.sub(r"ALLOWED_HOSTS\s*=\s*\[.*?\]", f"ALLOWED_HOSTS = ['{railway_domain}', 'localhost', '127.0.0.1']", settings_content, flags=re.DOTALL)
    else:
        settings_content += f"\nALLOWED_HOSTS = ['{railway_domain}', 'localhost', '127.0.0.1']\n"
    # CSRF_TRUSTED_ORIGINS
    if "CSRF_TRUSTED_ORIGINS" in settings_content:
        settings_content = re.sub(r"CSRF_TRUSTED_ORIGINS\s*=\s*\[.*?\]", f"CSRF_TRUSTED_ORIGINS = ['https://{railway_domain}']", settings_content, flags=re.DOTALL)
    else:
        settings_content += f"\nCSRF_TRUSTED_ORIGINS = ['https://{railway_domain}']\n"
    # Добавляем заголовки безопасности
    if "SECURE_PROXY_SSL_HEADER" not in settings_content:
        settings_content += "\nSECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')\nUSE_X_FORWARDED_HOST = True\n"
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write(settings_content)
    print("✅ settings.py обновлён (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, SSL)")
else:
    print("❌ settings.py не найден")

# 4. Коммитим и пушим
print("\n📦 Отправка изменений на GitHub...")
run_cmd("git add .")
run_cmd('git commit -m "Mobile fix: hide map on phones, show by button; fix CSRF settings"')
run_cmd("git push origin main")

print("\n🎉 Готово! Теперь:")
print("1. Перейдите на Railway → сервис crime-komi → вкладка Deployments → Redeploy.")
print("2. После перезапуска очистите кэш браузера на телефоне.")
print("3. Проверьте: на телефоне карта должна быть скрыта, появляться по кнопке «Показать карту».")