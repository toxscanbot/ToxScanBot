from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os
from PIL import Image
import pytesseract
import sqlite3

# Укажи путь к tesseract.exe (если Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Твой Telegram ID для получения отзывов
YOUR_TELEGRAM_ID = "6008650347"

# Ссылка для донатов (замени на свою)
DONATE_LINK = "https://example.com/donate"  # Например, Boosty

# Email для поддержки
SUPPORT_EMAIL = "toxscanbot@gmail.com"

# Функция для получения языка пользователя
def get_user_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    lang = context.user_data.get("lang")
    if not lang:
        # Автоопределение языка
        user_lang = update.message.from_user.language_code
        lang = "ru" if user_lang and user_lang.startswith("ru") else "en"
        context.user_data["lang"] = lang
        print(f"Автоопределён язык: {lang} для пользователя {update.message.from_user.id}")  # Отладка
    return lang

# Функция для получения информации об ингредиенте из базы
def get_ingredient_info(name: str, lang: str = "ru") -> tuple:
    conn = sqlite3.connect("toxscan.db")
    cursor = conn.cursor()
    cursor.execute("SELECT info, category FROM ingredients WHERE name = ? AND lang = ?", (name.lower(), lang))
    result = cursor.fetchone()
    conn.close()
    if result:
        info, category = result
        # Добавляем цветовую маркировку
        if category == "safe":
            return f"🟢 {info}", category
        elif category == "warning":
            return f"⚠️ {info}", category
        elif category == "danger":
            return f"🔴 {info}", category
    return "ℹ️ Нет данных." if lang == "ru" else "ℹ️ No data.", "unknown"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update, context)
    print(f"Команда /start для пользователя {update.message.from_user.id}, язык: {lang}")  # Отладка
    if lang == "ru":
        await update.message.reply_text(
            "👋 Привет! Я ToxScan — твой личный сканер составов еды и косметики 🧴🍫\n\n"
            "📦 Я анализирую:\n"
            "- 🍔 Продукты питания\n"
            "- 💄 Косметику\n\n"
            "🔍 Как это работает:\n"
            "- Пришли фото состава или напиши список ингредиентов\n"
            "- Я проверю их безопасность:\n"
            "  🟢 Безопасно\n"
            "  ⚠️ Спорно\n"
            "  🔴 Опасность\n"
            "- Получи рекомендации\n"
            "- Хочешь оставить отзыв? Просто напиши его!\n\n"
            f"🔥 Отправь фото или текст, выбери язык (/lang) или поддержи проект (/donate)!\n"
            f"📬 Связь: {SUPPORT_EMAIL}"
        )
    else:
        await update.message.reply_text(
            "👋 Hello! I'm ToxScan — your personal scanner for food and cosmetics 🧴🍫\n\n"
            "📦 I analyze:\n"
            "- 🍔 Food products\n"
            "- 💄 Cosmetics\n\n"
            "🔍 How it works:\n"
            "- Send a photo of the label or type a list of ingredients\n"
            "- I check their safety:\n"
            "  🟢 Safe\n"
            "  ⚠️ Questionable\n"
            "  🔴 Dangerous\n"
            "- Get recommendations\n"
            "- Want to leave feedback? Just write it!\n\n"
            f"🔥 Send a photo or text, choose language (/lang), or support the project (/donate)!\n"
            f"📬 Contact: {SUPPORT_EMAIL}"
        )

# Команда /lang с inline-кнопками
async def lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Команда /lang для пользователя {update.message.from_user.id}")  # Отладка
    keyboard = [
        [
            InlineKeyboardButton("Русский", callback_data="ru"),
            InlineKeyboardButton("English", callback_data="en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери язык:", reply_markup=reply_markup)

# Обработчик выбора языка через кнопку
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    new_lang = query.data
    context.user_data["lang"] = new_lang
    print(f"Язык установлен: {new_lang} для пользователя {query.from_user.id}")  # Отладка
    await query.edit_message_text(
        "Язык установлен: Русский" if new_lang == "ru" else "Language set: English"
    )

# Команда /list
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update, context)
    print(f"Команда /list для пользователя {update.message.from_user.id}, язык: {lang}")  # Отладка
    if lang == "ru":
        await update.message.reply_text("🔴 Топ вредных:\nФталаты\n⚠️ Спорные:\nПарабены, Сульфаты")
    else:
        await update.message.reply_text("🔴 Top harmful:\nPhthalates\n⚠️ Questionable:\nParabens, Sulfates")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update, context)
    print(f"Команда /help для пользователя {update.message.from_user.id}, язык: {lang}")  # Отладка
    if lang == "ru":
        await update.message.reply_text(
            "/start — Начать работу\n"
            "/lang — Выбрать язык\n"
            "/list — Топ вредных\n"
            "/help — Помощь и вопросы\n"
            "/donate — Поддержать проект\n"
            "/feedback — Отправить отзыв (или просто напиши его!)\n"
            "/privacy — Политика конфиденциальности"
        )
    else:
        await update.message.reply_text(
            "/start — Start the bot\n"
            "/lang — Choose language\n"
            "/list — Top harmful ingredients\n"
            "/help — Help and FAQ\n"
            "/donate — Support the project\n"
            "/feedback — Send feedback (or just write it!)\n"
            "/privacy — Privacy policy"
        )

# Команда /privacy
async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update, context)
    print(f"Команда /privacy для пользователя {update.message.from_user.id}, язык: {lang}")  # Отладка
    await update.message.reply_text(
        f"🔒 Политика: https://docs.google.com/document/d/1w2TC2fk-YkPErK1E_VJMZSK6FHb575bxfL3tIZeQql8/edit?usp=sharing\n"
        f"📬 Связь: {SUPPORT_EMAIL}"
        if lang == "ru"
        else f"🔒 Policy: https://docs.google.com/document/d/1w2TC2fk-YkPErK1E_VJMZSK6FHb575bxfL3tIZeQql8/edit?usp=sharing\n"
             f"📬 Contact: {SUPPORT_EMAIL}"
    )

# Команда /feedback (для явного ввода)
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update, context)
    print(f"Команда /feedback для пользователя {update.message.from_user.id}, язык: {lang}")  # Отладка
    if not context.args:
        await update.message.reply_text(
            f"Напиши отзыв или предложение после команды, например:\n/feedback Отличный бот!\n"
            f"Или просто отправь текст без команды!\n📬 Или пиши на {SUPPORT_EMAIL}"
            if lang == "ru"
            else f"Write feedback or a suggestion after the command, e.g.:\n/feedback Great bot!\n"
                 f"Or just send the text without the command!\n📬 Or contact {SUPPORT_EMAIL}"
        )
        return

    feedback_text = " ".join(context.args)
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Аноним"
    try:
        await context.bot.send_message(
            chat_id=YOUR_TELEGRAM_ID,
            text=f"📬 Новый отзыв от @{username} (ID: {user_id}):\n{feedback_text}"
        )
        await update.message.reply_text(
            f"Спасибо за отзыв! Он отправлен разработчику 😊\n📬 Связь: {SUPPORT_EMAIL}"
            if lang == "ru"
            else f"Thanks for the feedback! It has been sent to the developer 😊\n📬 Contact: {SUPPORT_EMAIL}"
        )
    except Exception as e:
        await update.message.reply_text(
            f"Ошибка при отправке отзыва: {e}\n📬 Попробуй написать на {SUPPORT_EMAIL}"
            if lang == "ru"
            else f"Error sending feedback: {e}\n📬 Try contacting {SUPPORT_EMAIL}"
        )

# Команда /donate
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update, context)
    print(f"Команда /donate для пользователя {update.message.from_user.id}, язык: {lang}")  # Отладка
    await update.message.reply_text(
        f"💖 Поддержи проект!\nПерейди по ссылке для доната: {DONATE_LINK}\n"
        f"📬 Связь: {SUPPORT_EMAIL}"
        if lang == "ru"
        else f"💖 Support the project!\nFollow the link to donate: {DONATE_LINK}\n"
             f"📬 Contact: {SUPPORT_EMAIL}"
    )

# Обработка текстовых сообщений (анализ ингредиентов или отзывов)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update, context)
    print(f"Текст от пользователя {update.message.from_user.id}, язык: {lang}, текст: {update.message.text}")  # Отладка
    text = update.message.text.strip()
    if text.startswith("/"):
        return  # Игнорируем команды

    # Проверяем, является ли текст списком ингредиентов (содержит запятую)
    if "," in text or " " in text.split()[-1]:  # Если есть запятая или это не одно слово
        composition = text.lower().split(", ")
        result = "🧪 Анализ:\n" if lang == "ru" else "🧪 Analysis:\n"
        for ing in composition:
            ing = ing.strip()
            if ing:
                info, _ = get_ingredient_info(ing, lang)
                result += f"- {ing}: {info}\n"
        await update.message.reply_text(result)
    else:
        # Считаем текст отзывом
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "Аноним"
        try:
            await context.bot.send_message(
                chat_id=YOUR_TELEGRAM_ID,
                text=f"📬 Новый отзыв от @{username} (ID: {user_id}):\n{text}"
            )
            await update.message.reply_text(
                f"Спасибо за отзыв! Он отправлен разработчику 😊\n📬 Связь: {SUPPORT_EMAIL}"
                if lang == "ru"
                else f"Thanks for the feedback! It has been sent to the developer 😊\n📬 Contact: {SUPPORT_EMAIL}"
            )
        except Exception as e:
            await update.message.reply_text(
                f"Ошибка при отправке отзыва: {e}\n📬 Попробуй написать на {SUPPORT_EMAIL}"
                if lang == "ru"
                else f"Error sending feedback: {e}\n📬 Try contacting {SUPPORT_EMAIL}"
            )

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update, context)
    print(f"Фото от пользователя {update.message.from_user.id}, язык: {lang}")  # Отладка
    await update.message.reply_chat_action("typing")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_path = f"photo_{update.message.from_user.id}.jpg"
        await photo_file.download_to_drive(photo_path)

        print("✅ Фото получено")
        await update.message.reply_text(
            "✅ Фото получено! Распознаю..." if lang == "ru"
            else "✅ Photo received! Analyzing..."
        )

        image = Image.open(photo_path)
        text = pytesseract.image_to_string(image, lang='rus+eng').lower()
        ingredients = [i.strip() for i in text.replace("\n", ", ").split(",")]

        result = "🧪 Результаты:\n" if lang == "ru" else "🧪 Results:\n"
        for ing in ingredients:
            if ing:
                info, _ = get_ingredient_info(ing, lang)
                result += f"- {ing}: {info}\n"

        await update.message.reply_text(result)
        os.remove(photo_path)

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {e}\n📬 Связь: {SUPPORT_EMAIL}"
            if lang == "ru"
            else f"Error: {e}\n📬 Contact: {SUPPORT_EMAIL}"
        )

# Запуск бота
def main():
    try:
        app = ApplicationBuilder().token("***REMOVED***").build()
        print("🤖 Бот успешно инициализирован")  # Отладка

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("lang", lang))
        app.add_handler(CallbackQueryHandler(set_language, pattern="^(ru|en)$"))
        app.add_handler(CommandHandler("list", list_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("donate", donate))
        app.add_handler(CommandHandler("feedback", feedback))
        app.add_handler(CommandHandler("privacy", privacy))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        print("🤖 Бот запущен")
        app.run_polling()
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")  # Отладка

if __name__ == "__main__":
    main()