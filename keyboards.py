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