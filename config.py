from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS").split(",")
APPOINTMENT_ID = os.getenv("APPOINTMENT_ID")
MAX_APPOINTMENT_DATE = os.getenv("MAX_APPOINTMENT_DATE")
if MAX_APPOINTMENT_DATE is None:
    MAX_APPOINTMENT_DATE = datetime.now().replace(year=datetime.now().year + 1).strftime('%Y-%m-%d')