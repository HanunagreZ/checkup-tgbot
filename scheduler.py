import schedule
import time
import threading
from telegram import Update
from bot_config import SCHEDULE_TIMES, FEELING_EMOJI
from keyboards import feeling_keyboard, yes_no_keyboard, observations_keyboard, main_menu_keyboard
from database import get_last_checkup


def setup_schedule(application):
    def send_morning_checkup():
        app = application
        for user_id in get_active_users():
            if not get_last_checkup(user_id, "morning"):
                app.bot.send_message(
                    chat_id=user_id,
                    text="Как твоё самочувствие?",
                    reply_markup=feeling_keyboard()
                )

    def send_afternoon_checkup():
        app = application
        for user_id in get_active_users():
            if not get_last_checkup(user_id, "afternoon"):
                app.bot.send_message(
                    chat_id=user_id,
                    text="Как твоё самочувствие?",
                    reply_markup=feeling_keyboard()
                )

    def send_evening_checkup():
        app = application
        for user_id in get_active_users():
            if not get_last_checkup(user_id, "evening"):
                app.bot.send_message(
                    chat_id=user_id,
                    text="Как твоё самочувствие?",
                    reply_markup=feeling_keyboard()
                )

    schedule.every().day.at(f"{SCHEDULE_TIMES['morning']:02d}:00").do(send_morning_checkup)
    schedule.every().day.at(f"{SCHEDULE_TIMES['afternoon']:02d}:00").do(send_afternoon_checkup)
    schedule.every().day.at(f"{SCHEDULE_TIMES['evening']:02d}:00").do(send_evening_checkup)


def run_scheduler(application):
    def run():
        while True:
            schedule.run_pending()
            time.sleep(60)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


active_users = set()


def register_user(user_id):
    active_users.add(user_id)


def get_active_users():
    return list(active_users)