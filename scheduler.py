import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from bot_config import SCHEDULE_TIMES
from keyboards import feeling_keyboard
from database import get_last_checkup


logger = logging.getLogger(__name__)
active_users = set()


def register_user(user_id):
    active_users.add(user_id)


def get_active_users():
    return list(active_users)


def send_scheduled_messages(updater, check_time):
    for user_id in get_active_users():
        if not get_last_checkup(user_id, check_time):
            try:
                updater.bot.send_message(
                    chat_id=user_id,
                    text="Как твоё самочувствие?",
                    reply_markup=feeling_keyboard()
                )
            except Exception as e:
                logger.error(f"Error sending message: {e}")


def setup_scheduler(updater):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        lambda: send_scheduled_messages(updater, "morning"),
        'cron',
        hour=SCHEDULE_TIMES['morning'],
        minute=0
    )

    scheduler.add_job(
        lambda: send_scheduled_messages(updater, "afternoon"),
        'cron',
        hour=SCHEDULE_TIMES['afternoon'],
        minute=0
    )

    scheduler.add_job(
        lambda: send_scheduled_messages(updater, "evening"),
        'cron',
        hour=SCHEDULE_TIMES['evening'],
        minute=0
    )

    scheduler.start()
    logger.info("Scheduler started")