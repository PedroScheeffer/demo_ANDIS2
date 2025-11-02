from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Project API"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()