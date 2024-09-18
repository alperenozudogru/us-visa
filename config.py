from dotenv import load_dotenv
import os

load_dotenv()

USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS").split(",")
THRESHOLD_DATE = os.getenv("THRESHOLD_DATE")
DRIVER_PATH = os.getenv("DRIVER_PATH")
APPOINTMENT_ID = os.getenv("APPOINTMENT_ID")