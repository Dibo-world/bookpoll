import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    DATABASE_URL: str     = os.getenv("DATABASE_URL")
    REDIS_URL: str        = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL")

settings = Settings()