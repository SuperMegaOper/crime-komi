import re
from pathlib import Path

BASE_HTML = Path("incidents/templates/incidents/base.html")
CSS_PATH = Path("incidents/static/incidents/css/style.css")

def backup_file(path):
    import shutil
    bak = path.with_suffix(path.suffix + ".finalbottom")
    shutil.copy2(path, bak)
    print(f"Резервная копия: {bak.name}")

# 1. Перемещаем кнопку в конец .sidebar и делаем toggle
if BASE_HTML.exists():
    backup_file(BASE_HTML)
    with open(BASE_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Удаляем все существующие кнопки (show, close, toggle)
    content = re.sub(r'<button[^>]*?(?:show-map-btn|close-map-btn|toggle-map-btn)[^>]*?>.*?</button>', '', content, flags=re.DOTALL)
    
    # Находим конец .sidebar (перед закрывающим </div>)
    # Вставляем кнопку в самый низ sidebar
    button_html = '<button class="toggle-map-btn" id="toggleMapBtn">📱 Показать карту</button>'
    if '<div class="sidebar">' in content:
        # Вставляем перед закрывающим </div> sidebar
        content = content.replace('</div>\n        </div>\n        <div class="map-container">', button_html + '\n        </div>\n        </div>\n        <div class="map-container">')
    
    # Обновляем скрипт
    script = '''
<script>
    (function() {
        var mapContainer = document.querySelector('.map-container');
        var toggleBtn = document.getElementById('toggleMapBtn');
        if (toggleBtn && mapContainer) {
            toggleBtn.addEventListener('click', function() {
                if (mapContainer.classList.contains('active')) {
                    mapContainer.classList.remove('active');
                    toggleBtn.textContent = "📱 Показать карту";
                } else {
                    mapContainer.classList.add('active');
                    toggleBtn.textContent = "✕ Закрыть карту";
                    if (window.map) { setTimeout(function() { window.map.invalidateSize(); }, 100); }
                }
            });
        }
    })();
</script>
'''
    if '</body>' in content:
        content = content.replace('</body>', script + '\n</body>')
    
    with open(BASE_HTML, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Кнопка перемещена вниз, реализован toggle")

# 2. Обновляем CSS: убираем старые стили, добавляем для toggle
if CSS_PATH.exists():
    backup_file(CSS_PATH)
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        css = f.read()
    
    # Удаляем старые стили кнопок
    css = re.sub(r'\.(show-map-btn|close-map-btn)\s*\{[^}]*\}', '', css, flags=re.DOTALL)
    
    # Добавляем стили для toggle кнопки (внизу)
    toggle_css = """
.toggle-map-btn {
    display: block;
    width: 100%;
    background: #c0392b;
    color: white;
    border: none;
    border-radius: 40px;
    padding: 10px;
    margin-top: 20px;
    font-size: 1rem;
    cursor: pointer;
}
@media (min-width: 769px) {
    .toggle-map-btn {
        display: none;
    }
}
"""
    if '.toggle-map-btn' not in css:
        css += toggle_css
    else:
        css = re.sub(r'\.toggle-map-btn\s*\{[^}]*\}', toggle_css, css, flags=re.DOTALL)
    
    with open(CSS_PATH, "w", encoding="utf-8") as f:
        f.write(css)
    print("✅ CSS обновлён: кнопка внизу, скрывается на десктопе")

print("\n🎉 Готово! Теперь кнопка одна, находится внизу боковой панели, открывает/закрывает карту.")
print("Выполните команды для отправки на GitHub:")
print("git add .")
print('git commit -m "Toggle map button at bottom of sidebar"')
print("git push origin main --force-with-lease")