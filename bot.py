import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters,
)
from groq import Groq

# --- Завантажуємо токени з файлу .env ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")   # безкоштовна модель Groq

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# --- Клієнт Groq (якщо ключ заданий) ---
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- Тексти пунктів меню ---
STUDENT_INFO = (
    "👤 *Студент*\n"
    "ПІБ: Матвєєв Володимир Валентинович\n"
    "Група: ІА-з31\n"
    "Варіант: 13"
)

IT_INFO = (
    "💻 *IT-технології*\n"
    "Мова: C# (.NET)\n"
    "Backend: ASP.NET Core, REST API\n"
    "Бази даних: PostgreSQL, MSSQL, Oracle\n"
    "Інфраструктура: Docker\n"
    "Desktop: WPF / XAML (MVVM), MAUI, WinForms"
)

CONTACTS_INFO = (
    "📞 *Контакти*\n"
    "Телефон: +380 97 630 44 32\n"
    "E-mail: v.zubich@gmail.com"
)

# --- Кнопки меню ---
MENU = ["👤 Студент", "💻 IT-технології", "📞 Контакти", "🤖 Prompt AI"]
keyboard = ReplyKeyboardMarkup(
    [[MENU[0], MENU[1]], [MENU[2], MENU[3]]],
    resize_keyboard=True,
)


# --- /start: показуємо меню ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = False
    await update.message.reply_text(
        "Вітаю! Це бот лабораторної роботи №3. Оберіть пункт меню 👇",
        reply_markup=keyboard,
    )


# --- Основний обробник повідомлень ---
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "👤 Студент":
        context.user_data["ai_mode"] = False
        await update.message.reply_text(STUDENT_INFO, parse_mode="Markdown", reply_markup=keyboard)

    elif text == "💻 IT-технології":
        context.user_data["ai_mode"] = False
        await update.message.reply_text(IT_INFO, parse_mode="Markdown", reply_markup=keyboard)

    elif text == "📞 Контакти":
        context.user_data["ai_mode"] = False
        await update.message.reply_text(CONTACTS_INFO, parse_mode="Markdown", reply_markup=keyboard)

    elif text == "🤖 Prompt AI":
        context.user_data["ai_mode"] = True
        await update.message.reply_text(
            "Напишіть ваше запитання до AI 👇 (щоб вийти — оберіть інший пункт меню)",
            reply_markup=keyboard,
        )

    elif context.user_data.get("ai_mode"):
        # будь-який текст у режимі AI відправляємо до Groq
        if not groq_client:
            await update.message.reply_text(
                "AI не налаштований. Додайте GROQ_API_KEY у файл .env", reply_markup=keyboard
            )
            return
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        try:
            resp = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": text}],
            )
            answer = resp.choices[0].message.content
        except Exception as e:
            answer = f"Помилка запиту до AI: {e}"
        await update.message.reply_text(answer, reply_markup=keyboard)

    else:
        await update.message.reply_text("Оберіть пункт меню 👇", reply_markup=keyboard)


def main():
    if not TELEGRAM_TOKEN:
        raise SystemExit("Немає TELEGRAM_TOKEN. Додайте його у файл .env")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Бот запущено. Зупинка — Ctrl+C.")
    app.run_polling()


if __name__ == "__main__":
    main()
