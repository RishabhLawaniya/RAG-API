from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "RAG Document API"
    DEBUG: bool = False
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = ""
    SYNC_DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    GROQ_API_KEY: str = ""

    db_username: str
    db_password: str
    db_host: str

    class Config:
        env_file = ".env"

settings = Settings()