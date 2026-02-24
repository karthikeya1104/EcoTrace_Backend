import os
from dotenv import load_dotenv

load_dotenv()

APP_BASE_URL = os.getenv("APP_BASE_URL")

if not APP_BASE_URL:
    raise RuntimeError("APP_BASE_URL is not set in environment")
