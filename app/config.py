from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    app_name = os.getenv("APP_NAME", "Eco Tourism Management Portal")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./eco_tourism.db")
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
    algorithm = os.getenv("ALGORITHM", "HS256")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

settings = Settings()

