import asyncio
from datetime import datetime
from bot_config import SCHEDULE_TIMES
from keyboards import feeling_keyboard
from database import get_last_checkup


app_ref = None
active_users = set()


def register_user(user_id):
    active_users.add(user_id)


def get_active_users():
    return list(active_users)


async def send_scheduled_messages():
    while True:
        now = datetime.now()
        current_hour = now.hour

        for check_time, hour in SCHEDULE_TIMES.items():
            if current_hour == hour:
                if app_ref:
                    for user_id in get_active_users():
                        if not get_last_checkup(user_id, check_time):
                            try:
                                await app_ref.bot.send_message(
                                    chat_id=user_id,
                                    text="Как твоё самочувствие?",
                                    reply_markup=feeling_keyboard()
                                )
                            except Exception:
                                pass

        await asyncio.sleep(60)


async def run_scheduler():
    await send_scheduled_messages()


def setup_scheduler(application):
    global app_ref
    app_ref = application