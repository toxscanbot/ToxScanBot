from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
from PIL import Image
import pytesseract

# Укажи путь к tesseract.exe (если Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# База ингредиентов
INGREDIENTS_DB = {
    "парабены": "⚠️ Потенциально вредны",
    "сульфаты": "⚠️ Могут раздражать кожу",
    "фталаты": "⚠️ Нарушают гормоны",
    "вода": "✅ Безопасный ингредиент",
    "сахар": "✅ Безопасный (в еде)",
    "лимонная кислота": "✅ Безопасный консервант"
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я ToxScan.\n"
        "📸 Пришли фото состава или используй /check ингредиенты вручную."
    )

# Команда /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши ингредиенты после команды, например:\n/check вода, сахар")
        return

    composition = " ".join(context.args).lower().split(", ")
    result = "🧪 Анализ:\n"
    for ing in composition:
        info = INGREDIENTS_DB.get(ing.strip(), "ℹ️ Нет информации.")
        result += f"- {ing.strip()}: {info}\n"

    await update.message.reply_text(result)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — Начать работу\n"
        "/check — Проверка вручную\n"
        "/scan — Фото состава\n"
        "/privacy — Политика\n"
        "/list — Топ вредных"
    )

# Команда /privacy
async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔒 Политика: https://docs.google.com/...")

# Команда /list
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Топ вредных:\nПарабены, Сульфаты, Фталаты")

# Команда /scan
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Пришли фото, я начну анализ.")

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_path = f"photo_{update.message.from_user.id}.jpg"
        await photo_file.download_to_drive(photo_path)

        print("✅ Фото получено")
        await update.message.reply_text("✅ Фото получено! Распознаю...")

        image = Image.open(photo_path)
        text = pytesseract.image_to_string(image, lang='rus+eng').lower()
        ingredients = [i.strip() for i in text.replace("\n", ", ").split(",")]

        result = "🧪 Результаты:\n"
        for ing in ingredients:
            if ing:
                info = INGREDIENTS_DB.get(ing, "ℹ️ Нет данных.")
                result += f"- {ing}: {info}\n"

        await update.message.reply_text(result)
        os.remove(photo_path)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Запуск бота
def main():
    app = ApplicationBuilder().token("***REMOVED***").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("privacy", privacy))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()