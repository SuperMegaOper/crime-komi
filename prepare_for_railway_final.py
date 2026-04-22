import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
BASE_HTML = PROJECT_DIR / "incidents" / "templates" / "incidents" / "base.html"
CSS_PATH = PROJECT_DIR / "incidents" / "static" / "incidents" / "css" / "style.css"

def backup_file(path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".mobiletoggle")
        shutil.copy2(path, bak)
        print(f"Резервная копия: {bak.name}")

# 1. Добавляем стили для мобильной версии (карта скрыта, кнопка видна)
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

# 2. Модифицируем base.html: добавляем кнопку и скрипт
if BASE_HTML.exists():
    backup_file(BASE_HTML)
    with open(BASE_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Находим блок .map-container и оборачиваем его в дополнительный div (или добавляем кнопку рядом)
    # Добавляем кнопку перед map-container (или после)
    button_html = '<button class="show-map-btn" id="showMapBtn">📱 Показать карту</button>\n'
    close_button = '<button class="close-map-btn" id="closeMapBtn">✕ Закрыть</button>\n'
    
    # Вставляем кнопку после sidebar (или в нужное место)
    if '<div class="map-container">' in content:
        # Вставляем кнопку перед map-container
        content = content.replace('<div class="map-container">', button_html + '<div class="map-container">')
        # Вставляем кнопку закрытия внутри map-container
        content = content.replace('<div id="map"></div>', close_button + '<div id="map"></div>')
    
    # Добавляем JavaScript для переключения
    js_script = """
<script>
    (function() {
        var mapContainer = document.querySelector('.map-container');
        var showBtn = document.getElementById('showMapBtn');
        var closeBtn = document.getElementById('closeMapBtn');
        if (showBtn) {
            showBtn.addEventListener('click', function() {
                mapContainer.classList.add('active');
                // принудительно обновляем размер карты, если она уже инициализирована
                if (window.map) {
                    setTimeout(function() { window.map.invalidateSize(); }, 100);
                }
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
    if '</body>' in content:
        content = content.replace('</body>', js_script + '\n</body>')
    
    with open(BASE_HTML, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ base.html обновлён: добавлена кнопка показа карты и скрипт")
else:
    print("❌ base.html не найден")

print("\n🎉 Готово! Теперь на мобильных устройствах карта скрыта, появляется по кнопке «Показать карту».")
print("Не забудьте закоммитить изменения и запушить на GitHub, затем перезапустить деплой на Railway.")