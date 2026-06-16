import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv(Path(__file__).parent.parent / ".env")


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/recipe_db"
    )

    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")

    
    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        "openai/gpt-4o-mini"
    )

    REQUEST_TIMEOUT: int = 30

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()