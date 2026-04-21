import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

EMOJI_POOL = ["😊", "😌", "😄", "🌸", "💪", "✨", "❤️", "🙂"]

FEELING_EMOJI = {
    "bad": "😔",
    "neutral": "😐",
    "good": "😄"
}

RESPONSE_COLORS = {
    "good": "🟢",
    "neutral": "🟡",
    "bad": "🔴"
}

SCHEDULE_TIMES = {
    "morning": 8,
    "afternoon": 14,
    "evening": 20
}

DB_PATH = "checkup.db"
