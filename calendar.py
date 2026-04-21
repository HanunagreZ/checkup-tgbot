from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from calendar import monthrange
from config import RESPONSE_COLORS


def build_calendar(dates):
    today = datetime.now()
    year = today.year
    month = today.month

    _, last_day = monthrange(year, month)

    keyboard = []

    month_names = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    keyboard.append([InlineKeyboardButton(f"{month_names[month-1]} {year}", callback_data="calendar:month")])

    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.append([InlineKeyboardButton(day, callback_data="calendar:skip") for day in week_days])

    first_day = datetime(year, month, 1)
    first_weekday = first_day.weekday()

    days = []
    for _ in range(first_weekday):
        days.append(InlineKeyboardButton(" ", callback_data="calendar:skip"))

    date_map = {date_str: feeling for date_str, feeling in dates}

    for day in range(1, last_day + 1):
        date_iso = f"{year}-{month:02d}-{day:02d}"

        if date_iso in date_map:
            feeling = date_map[date_iso]
            color_emoji = RESPONSE_COLORS.get(feeling, "⚪")
            days.append(InlineKeyboardButton(
                f"{color_emoji}{day}",
                callback_data=f"calendar:{date_iso}"
            ))
        else:
            days.append(InlineKeyboardButton(str(day), callback_data="calendar:skip"))

    rows = [days[i:i+7] for i in range(0, len(days), 7)]
    keyboard.extend(rows)

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu:back")])

    return InlineKeyboardMarkup(keyboard)


def build_day_detail(date_str: str, checkups):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt.strftime("%d.%m.%Y")
    except:
        formatted_date = date_str

    feeling_map = {"good": "Хорошо", "neutral": "Нейтрально", "bad": "Плохо"}
    yes_no_map = {"yes": "Да", "no": "Нет"}

    lines = [f"📊 *{formatted_date}*"]

    time_map = {
        "morning": "🌅 Утро (8:00)",
        "afternoon": "🌞 День (14:00)",
        "evening": "🌙 Вечер (20:00)"
    }

    for checkup in checkups:
        check_date, check_time, feeling, gluten, matcha_coffee, work_stress, general_stress, observations = checkup

        time_label = time_map.get(check_time, check_time)
        feeling_label = feeling_map.get(feeling, feeling)

        lines.append(f"\n{time_label}")
        lines.append(f"  Самочувствие: {feeling_label}")

        if check_time == "evening":
            if gluten:
                lines.append(f"  Глютен: {yes_no_map.get(gluten, gluten)}")
            if matcha_coffee:
                lines.append(f"  Матча/кофе: {yes_no_map.get(matcha_coffee, matcha_coffee)}")
            if work_stress:
                lines.append(f"  Стресс (работа): {yes_no_map.get(work_stress, work_stress)}")
            if general_stress:
                lines.append(f"  Стресс (общий): {yes_no_map.get(general_stress, general_stress)}")
            if observations:
                lines.append(f"  Заметки: {observations}")

    return "\n".join(lines)