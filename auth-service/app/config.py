import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET: str   = os.getenv("JWT_SECRET")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", 24))

settings = Settings()