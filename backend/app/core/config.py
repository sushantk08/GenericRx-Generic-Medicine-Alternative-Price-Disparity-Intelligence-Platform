import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "GenericRx API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Configuration
    PG_USER: str = os.getenv("POSTGRES_USER", "genericrx")
    PG_PASS: str = os.getenv("POSTGRES_PASSWORD", "")
    PG_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    PG_PORT: str = os.getenv("POSTGRES_PORT", "5433")
    PG_DB: str = os.getenv("POSTGRES_DB", "genericrx_db")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    # Allowed CORS Origins (allowing Next.js frontend)
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        case_sensitive = True


settings = Settings()