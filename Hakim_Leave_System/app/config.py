import os
APP_NAME = os.getenv("APP_NAME", "Hakim Platform")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Riyadh")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hakim_leave.db")
