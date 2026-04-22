import re
from pathlib import Path

BASE_HTML = Path("incidents/templates/incidents/base.html")
CSS_PATH = Path("incidents/static/incidents/css/style.css")

def backup_file(path):
    if path.exists():
        import shutil
        bak = path.with_suffix(path.suffix + ".togglebak")
        shutil.copy2(path, bak)
        print(f"Резервная копия: {bak.name}")

# 1. Обновляем base.html: одна кнопка-переключатель
if BASE_HTML.exists():
    backup_file(BASE_HTML)
    with open(BASE_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Удаляем все старые кнопки (show и close)
    content = re.sub(r'<button class="show-map-btn".*?</button>', '', content, flags=re.DOTALL)
    content = re.sub(r'<button class="close-map-btn".*?</button>', '', content, flags=re.DOTALL)
    
    # Добавляем одну кнопку-переключатель в нужное место (перед map-container)
    toggle_button = '<button class="toggle-map-btn" id="toggleMapBtn">📱 Показать карту</button>\n'
    if '<div class="map-container">' in content:
        content = content.replace('<div class="map-container">', toggle_button + '<div class="map-container">')
    
    # Добавляем новый скрипт для toggle
    script = '''
<script>
    (function() {
        var mapContainer = document.querySelector('.map-container');
        var toggleBtn = document.getElementById('toggleMapBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                if (mapContainer.classList.contains('active')) {
                    mapContainer.classList.remove('active');
                    toggleBtn.innerHTML = "📱 Показать карту";
                } else {
                    mapContainer.classList.add('active');
                    toggleBtn.innerHTML = "✕ Закрыть карту";
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
    print("✅ base.html обновлён: одна кнопка-переключатель")

# 2. Обновляем CSS: убираем лишние стили для close-btn, добавляем для toggle
if CSS_PATH.exists():
    backup_file(CSS_PATH)
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        css = f.read()
    
    # Удаляем стили для .close-map-btn, добавим .toggle-map-btn
    css = re.sub(r'\.close-map-btn\s*\{[^}]*\}', '', css, flags=re.DOTALL)
    # Добавим стили для toggle кнопки
    toggle_css = """
.toggle-map-btn {
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
    print("✅ CSS обновлён: одна кнопка-переключатель")

print("\n🎉 Готово! Теперь карта открывается и закрывается одной кнопкой.")
print("Выполните команды для отправки на GitHub:")
print("git add .")
print('git commit -m "Toggle map button: one button shows/hides map"')
print("git push origin main --force-with-lease")