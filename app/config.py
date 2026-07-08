import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

TIMEZONE = ZoneInfo(os.getenv("TIMEZONE", "Asia/Yakutsk"))

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

DB_NAME = os.getenv("DB_NAME", "kakashi.db")
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, DB_NAME)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Когда напоминать (20:00)
REMINDER_HOUR = 20
REMINDER_MINUTE = 0

# Когда проверять (23:59)
CHECK_HOUR = 23
CHECK_MINUTE = 59

# День недели генерации расписания
SCHEDULE_DAY = "sunday"

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))