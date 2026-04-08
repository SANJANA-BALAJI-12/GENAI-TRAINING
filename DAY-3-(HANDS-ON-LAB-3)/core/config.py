from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "HITL Content Moderation System"
    groq_api_key: str
    model_name: str = "llama-3.1-8b-instant"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
