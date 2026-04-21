import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from bot_config import TELEGRAM_BOT_TOKEN
from database import init_db, add_user
from handlers import handle_callback, handle_message, show_calendar, show_day_detail
from keyboards import main_menu_keyboard
from scheduler import register_user


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def health_check(request):
    return web.Response(text="OK")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name, user.last_name)
    register_user(user.id)

    await update.message.reply_text(
        "Привет! Я буду следить за твоим самочувствием. "
        "Три раза в день буду спрашивать, как ты себя чувствуешь.\n\n"
        "Используй /report чтобы посмотреть отчёт.",
        reply_markup=main_menu_keyboard()
    )


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await show_calendar(update, context, user_id)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я буду присылать тебе вопросы о самочувствии в 8:00, 14:00 и 20:00.\n\n"
        "Команды:\n"
        "/start - Начать\n"
        "/report - Посмотреть отчёт\n"
        "/help - Помощь"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling update: {context.error}")


async def main():
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
    app.add_error_handler(error_handler)

    logger.info("Бот запущен")

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    web_app = web.Application()
    web_app.router.add_get('/', health_check)
    web_app.router.add_get('/health', health_check)

    runner = web.AppRunner(web_app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    logger.info(f"HTTP server started on port {port}")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
