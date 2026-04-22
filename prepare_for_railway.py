import re
from pathlib import Path

BASE_HTML = Path("incidents/templates/incidents/base.html")
CSS_PATH = Path("incidents/static/incidents/css/style.css")

def backup_file(path):
    if path.exists():
        import shutil
        bak = path.with_suffix(path.suffix + ".movebtn")
        shutil.copy2(path, bak)
        print(f"Резервная копия: {bak.name}")

# 1. Перемещаем кнопку карты в конец сайдбара
if BASE_HTML.exists():
    backup_file(BASE_HTML)
    with open(BASE_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Находим кнопку и перемещаем её в самый конец .sidebar
    # Ищем div с классом sidebar
    sidebar_pattern = r'(<div class="sidebar">)(.*?)(</div>)'
    match = re.search(sidebar_pattern, content, re.DOTALL)
    if match:
        sidebar_open = match.group(1)
        sidebar_content = match.group(2)
        sidebar_close = match.group(3)
        # Ищем кнопку в sidebar_content
        button_pattern = r'(<button class="toggle-map-btn".*?</button>)'
        button_match = re.search(button_pattern, sidebar_content, re.DOTALL)
        if button_match:
            button = button_match.group(1)
            # Удаляем кнопку из текущего места и добавляем в конец
            sidebar_content = re.sub(button_pattern, '', sidebar_content, flags=re.DOTALL)
            # Добавляем в конец
            sidebar_content += '\n' + button
            new_sidebar = sidebar_open + sidebar_content + sidebar_close
            content = re.sub(sidebar_pattern, new_sidebar, content, flags=re.DOTALL)
            print("✅ Кнопка карты перемещена в конец сайдбара")
        else:
            print("⚠️ Кнопка не найдена")
    else:
        print("❌ Не найден .sidebar")
    
    with open(BASE_HTML, "w", encoding="utf-8") as f:
        f.write(content)

# 2. Добавим в админ-панель улучшенное отображение анонимных сообщений
admin_path = Path("incidents/admin.py")
if admin_path.exists():
    backup_file(admin_path)
    with open(admin_path, "r", encoding="utf-8") as f:
        admin_content = f.read()
    # Проверяем, есть ли уже настройка для AnonymousReport
    if 'class AnonymousReportAdmin' not in admin_content:
        # Добавляем улучшенный admin
        new_admin = '''
@admin.register(AnonymousReport)
class AnonymousReportAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'location')
    list_filter = ('created_at',)
    search_fields = ('subject', 'message', 'location')
    readonly_fields = ('subject', 'message', 'location', 'created_at')
    ordering = ('-created_at',)
'''
        # Вставляем перед последней строкой или в конец
        admin_content += new_admin
        with open(admin_path, "w", encoding="utf-8") as f:
            f.write(admin_content)
        print("✅ Админ-панель для анонимных сообщений улучшена")
    else:
        print("⚠️ Админ-панель уже настроена")
else:
    print("❌ admin.py не найден")

print("\n🎉 Готово! Теперь кнопка карты внизу.")
print("Выполните git add . && git commit -m 'Move map button to bottom' && git push origin main --force-with-lease")