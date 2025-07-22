import sqlite3

# Создание базы данных
conn = sqlite3.connect("toxscan.db")
cursor = conn.cursor()

# Создание таблицы ингредиентов с новым полем category
cursor.execute("""
CREATE TABLE IF NOT EXISTS ingredients (
    name TEXT PRIMARY KEY,
    info TEXT NOT NULL,
    lang TEXT NOT NULL,
    category TEXT NOT NULL
)
""")

# Начальные данные
ingredients = [
    ("вода", "Безопасный ингредиент", "ru", "safe"),
    ("сахар", "Безопасный (в еде)", "ru", "safe"),
    ("лимонная кислота", "Безопасный консервант", "ru", "safe"),
    ("парабены", "Потенциально вредны, могут вызывать раздражение", "ru", "warning"),
    ("сульфаты", "Могут раздражать кожу (SLES)", "ru", "warning"),
    ("фталаты", "Нарушают гормоны, потенциально токсичны", "ru", "danger"),
    ("water", "Safe ingredient", "en", "safe"),
    ("sugar", "Safe (in food)", "en", "safe"),
    ("citric acid", "Safe preservative", "en", "safe"),
    ("parabens", "Potentially harmful, may cause irritation", "en", "warning"),
    ("sulfates", "May irritate skin (SLES)", "en", "warning"),
    ("phthalates", "Hormone disruptor, potentially toxic", "en", "danger")
]

# Заполняем таблицу
cursor.executemany("INSERT OR IGNORE INTO ingredients (name, info, lang, category) VALUES (?, ?, ?, ?)", ingredients)

# Сохраняем и закрываем
conn.commit()
conn.close()

print("✅ База toxscan.db создана и заполнена!")