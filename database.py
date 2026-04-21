import sqlite3
from datetime import date, datetime
from bot_config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            check_date TEXT,
            check_time TEXT,
            feeling TEXT,
            gluten TEXT,
            matcha_coffee TEXT,
            work_stress TEXT,
            general_stress TEXT,
            observations TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, registered_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, first_name, last_name, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def save_checkup(user_id, check_time, feeling, gluten=None, matcha_coffee=None,
                work_stress=None, general_stress=None, observations=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute("""
        INSERT INTO checkups (user_id, check_date, check_time, feeling, gluten,
                             matcha_coffee, work_stress, general_stress, observations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, today, check_time, feeling, gluten, matcha_coffee,
          work_stress, general_stress, observations))

    conn.commit()
    conn.close()


def get_user_checkups(user_id, check_date=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if check_date:
        cursor.execute("""
            SELECT check_date, check_time, feeling, gluten, matcha_coffee,
                   work_stress, general_stress, observations
            FROM checkups
            WHERE user_id = ? AND check_date = ?
            ORDER BY check_time
        """, (user_id, check_date))
    else:
        cursor.execute("""
            SELECT check_date, check_time, feeling, gluten, matcha_coffee,
                   work_stress, general_stress, observations
            FROM checkups
            WHERE user_id = ?
            ORDER BY check_date DESC, check_time
        """, (user_id,))

    results = cursor.fetchall()
    conn.close()

    return results


def get_checkup_dates(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT check_date, feeling
        FROM checkups
        WHERE user_id = ?
        GROUP BY check_date
        ORDER BY check_date DESC
    """, (user_id,))

    results = cursor.fetchall()
    conn.close()

    return results


def get_last_checkup(user_id, check_time):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute("""
        SELECT feeling, gluten, matcha_coffee, work_stress, general_stress, observations
        FROM checkups
        WHERE user_id = ? AND check_date = ? AND check_time = ?
    """, (user_id, today, check_time))

    result = cursor.fetchone()
    conn.close()

    return result