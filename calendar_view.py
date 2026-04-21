from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from calendar import monthrange
from bot_config import RESPONSE_COLORS, FEELING_EMOJI
from database import get_day_feeling, get_week_checkups


def build_calendar(user_id, dates):
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

    for day in range(1, last_day + 1):
        date_iso = f"{year}-{month:02d}-{day:02d}"

        feeling = get_day_feeling(user_id, date_iso)
        if feeling:
            emoji = FEELING_EMOJI.get(feeling, "⚪")
            days.append(InlineKeyboardButton(
                f"{emoji}{day}",
                callback_data=f"calendar:{date_iso}"
            ))
        else:
            days.append(InlineKeyboardButton(str(day), callback_data="calendar:skip"))

    rows = [days[i:i+7] for i in range(0, len(days), 7)]
    keyboard.extend(rows)

    keyboard.append([
        InlineKeyboardButton("📆 Неделя", callback_data="calendar:week:0")
    ])

    return InlineKeyboardMarkup(keyboard)


def build_week_report(user_id, weeks_ago=0):
    week_start, week_end, checkups = get_week_checkups(user_id, weeks_ago)

    if not checkups:
        return f"За неделю {week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m')} нет данных."

    feeling_map = {"good": "Хорошо", "neutral": "Нейтрально", "bad": "Плохо"}
    yes_no_map = {"yes": "Да", "no": "Нет"}
    time_map = {
        "morning": "🌅 Утро",
        "afternoon": "🌞 День",
        "evening": "🌙 Вечер"
    }

    lines = [f"📆 Неделя {week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m')}"]

    current_date = None
    day_data = {}

    for checkup in checkups:
        check_date_str, check_time, feeling, gluten, matcha_coffee, work_stress, general_stress, observations = checkup

        if check_date_str != current_date:
            if current_date and day_data:
                dt = datetime.strptime(current_date, "%Y-%m-%d")
                lines.append(f"\n📅 {dt.strftime('%d.%m')}")
                for t, f in day_data.items():
                    lines.append(f"  {time_map.get(t, t)}: {feeling_map.get(f, f)}")
                day_data = {}
            current_date = check_date_str

        day_data[check_time] = feeling

    if current_date and day_data:
        dt = datetime.strptime(current_date, "%Y-%m-%d")
        lines.append(f"\n📅 {dt.strftime('%d.%m')}")
        for t, f in day_data.items():
            lines.append(f"  {time_map.get(t, t)}: {feeling_map.get(f, f)}")

    bad_count = sum(1 for c in checkups if c[2] == "bad")
    neutral_count = sum(1 for c in checkups if c[2] == "neutral")
    good_count = sum(1 for c in checkups if c[2] == "good")

    lines.append(f"\n📊 Всего: 🟢{good_count} 🟡{neutral_count} 🔴{bad_count}")

    return "\n".join(lines)


def build_day_detail(date_str: str, checkups):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt.strftime("%d.%m.%Y")
    except:
        formatted_date = date_str

    feeling_map = {"good": "Хорошо", "neutral": "Нейтрально", "bad": "Плохо"}
    yes_no_map = {"yes": "Да", "no": "Нет"}

    time_order = {"morning": 1, "afternoon": 2, "evening": 3}
    checkups = sorted(checkups, key=lambda x: time_order.get(x[1], 0))

    lines = [f"📊 *{formatted_date}*"]

    time_map = {
        "morning": "🌅 Утро (8:00)",
        "afternoon": "🌞 День (14:00)",
        "evening": "🌙 Вечер (20:00)"
    }

    evening_data = None
    evening_checked = False

    for checkup in checkups:
        check_date, check_time, feeling, gluten, matcha_coffee, work_stress, general_stress, observations = checkup

        time_label = time_map.get(check_time, check_time)
        feeling_label = feeling_map.get(feeling, feeling)

        if check_time == "evening" and not evening_checked:
            evening_data = checkup
            evening_checked = True
            continue

        lines.append(f"\n{time_label}")
        lines.append(f"  Самочувствие: {feeling_label}")

    if evening_data:
        lines.append(f"\n{time_map['evening']}")
        lines.append(f"  Самочувствие: {feeling_map.get(evening_data[2], evening_data[2])}")
        if evening_data[3]:
            lines.append(f"  Глютен: {yes_no_map.get(evening_data[3], evening_data[3])}")
        if evening_data[4]:
            lines.append(f"  Матча/кофе: {yes_no_map.get(evening_data[4], evening_data[4])}")
        if evening_data[5]:
            lines.append(f"  Стресс (работа): {yes_no_map.get(evening_data[5], evening_data[5])}")
        if evening_data[6]:
            lines.append(f"  Стресс (общий): {yes_no_map.get(evening_data[6], evening_data[6])}")
        if evening_data[7]:
            lines.append(f"  Заметки: {evening_data[7]}")

    return "\n".join(lines)
