from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot_config import FEELING_EMOJI


def feeling_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{FEELING_EMOJI['bad']} Плохо", callback_data="feeling:bad"),
            InlineKeyboardButton(f"{FEELING_EMOJI['neutral']} Нейтрально", callback_data="feeling:neutral"),
            InlineKeyboardButton(f"{FEELING_EMOJI['good']} Хорошо", callback_data="feeling:good")
        ]
    ])


def yes_no_keyboard(callback_prefix):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Да", callback_data=f"{callback_prefix}:yes"),
            InlineKeyboardButton("❌ Нет", callback_data=f"{callback_prefix}:no")
        ]
    ])


def observations_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Да", callback_data="observations:yes"),
            InlineKeyboardButton("🚫 Нет", callback_data="observations:no")
        ]
    ])


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Отчёт", callback_data="menu:report")]
    ])


def week_navigation_keyboard(current_week=0):
    buttons = []
    if current_week < 10:
        buttons.append(InlineKeyboardButton("◀️ Прошлая неделя", callback_data=f"calendar:week:{current_week + 1}"))
    if current_week > 0:
        buttons.append(InlineKeyboardButton("▶️ Эта неделя", callback_data=f"calendar:week:{current_week - 1}"))

    return InlineKeyboardMarkup([
        buttons,
        [InlineKeyboardButton("📅 К календарю", callback_data="menu:report")]
    ])