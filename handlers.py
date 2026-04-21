from telegram import Update
from telegram.ext import ContextTypes
from bot_config import FEELING_EMOJI, RESPONSE_COLORS
from database import save_checkup, get_last_checkup, get_checkup_dates, get_user_checkups
from keyboards import feeling_keyboard, yes_no_keyboard, observations_keyboard, main_menu_keyboard
from calendar_view import build_calendar, build_day_detail


class CheckupState:
    def __init__(self):
        self.step = "start"
        self.check_time = None
        self.feeling = None
        self.gluten = None
        self.matcha_coffee = None
        self.work_stress = None
        self.general_stress = None
        self.observations = None


user_states = {}


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    
    data = query.data
    user_id = update.effective_user.id

    await query.answer()

    if data == "menu:report":
        await show_calendar(update, context, user_id)
        return

    if data.startswith("calendar:"):
        date_str = data.replace("calendar:", "")
        await show_day_detail(update, context, user_id, date_str)
        return

    if user_id not in user_states:
        user_states[user_id] = CheckupState()

    state = user_states[user_id]

    if data.startswith("feeling:"):
        state.feeling = data.split(":")[1]
        save_checkup(user_id, state.check_time, state.feeling)

        if state.check_time == "evening":
            await query.edit_message_text(
                "Ела сегодня глютен?",
                reply_markup=yes_no_keyboard("gluten")
            )
            state.step = "gluten"
        else:
            response_emoji = FEELING_EMOJI[state.feeling]
            await query.edit_message_text(
                f"{response_emoji} Зафиксировано! До следующего сообщения."
            )
            del user_states[user_id]

    elif data.startswith("gluten:"):
        state.gluten = data.split(":")[1]
        await query.edit_message_text(
            "Пила матчу / кофе?",
            reply_markup=yes_no_keyboard("matcha")
        )
        state.step = "matcha"

    elif data.startswith("matcha:"):
        state.matcha_coffee = data.split(":")[1]
        await query.edit_message_text(
            "Стрессовала из-за работы?",
            reply_markup=yes_no_keyboard("work_stress")
        )
        state.step = "work_stress"

    elif data.startswith("work_stress:"):
        state.work_stress = data.split(":")[1]
        await query.edit_message_text(
            "Стрессовала в общем?",
            reply_markup=yes_no_keyboard("general_stress")
        )
        state.step = "general_stress"

    elif data.startswith("general_stress:"):
        state.general_stress = data.split(":")[1]
        await query.edit_message_text(
            "Есть замечания?",
            reply_markup=observations_keyboard()
        )
        state.step = "observations"

    elif data.startswith("observations:"):
        value = data.split(":")[1]
        if value == "yes":
            state.step = "obs_text"
            await query.edit_message_text(
                "Напиши свои замечания:"
            )
        else:
            state.observations = None
            await finish_checkup(query, state)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text if update.message else None

    if not text:
        return

    if user_id not in user_states:
        return

    state = user_states[user_id]

    if state.step == "obs_text":
        state.observations = text
        await finish_checkup(update.message, state)


async def finish_checkup(message, state):
    user_id = message.chat.id

    save_checkup(
        user_id,
        state.check_time,
        state.feeling,
        state.gluten,
        state.matcha_coffee,
        state.work_stress,
        state.general_stress,
        state.observations
    )

    await message.reply_text("Ты ж моя умница! До завтра 😊")
    del user_states[user_id]


async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    dates = get_checkup_dates(user_id)

    if not dates:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "Пока нет записей.",
                reply_markup=main_menu_keyboard()
            )
        return

    calendar = build_calendar(dates)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "📅 Выбери день:",
            reply_markup=calendar
        )


async def show_day_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, date_str: str):
    checkups = get_user_checkups(user_id, date_str)

    if not checkups:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "Нет данных за этот день.",
                reply_markup=build_calendar(get_checkup_dates(user_id))
            )
        return

    detail = build_day_detail(date_str, checkups)
    if update.callback_query:
        await update.callback_query.edit_message_text(detail, parse_mode="Markdown")
