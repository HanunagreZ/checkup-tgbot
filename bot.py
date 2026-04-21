import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.ext import CallbackContext
from bot_config import TELEGRAM_BOT_TOKEN
from database import init_db, add_user
from handlers import handle_callback, handle_message, show_calendar, show_day_detail
from keyboards import main_menu_keyboard
from scheduler import register_user, setup_scheduler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def start_command(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name, user.last_name)
    register_user(user.id)

    update.message.reply_text(
        "Привет! Я буду следить за твоим самочувствием. "
        "Три раза в день буду спрашивать, как ты себя чувствуешь.\n\n"
        "Используй /report чтобы посмотреть отчёт.",
        reply_markup=main_menu_keyboard()
    )


def report_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    show_calendar(update, context, user_id)


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Я буду присылать тебе вопросы о самочувствии в 8:00, 14:00 и 20:00.\n\n"
        "Команды:\n"
        "/start - Начать\n"
        "/report - Посмотреть отчёт\n"
        "/help - Помощь"
    )


def main():
    init_db()

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    setup_scheduler(app)

    logger.info("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()