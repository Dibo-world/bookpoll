import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    DATABASE_URL: str     = os.getenv("DATABASE_URL")
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL")
    JWT_SECRET: str       = os.getenv("JWT_SECRET")

settings = Settings()