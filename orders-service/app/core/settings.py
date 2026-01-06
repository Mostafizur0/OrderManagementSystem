from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    LOGGER_NAME: str = "fastapi-orders-service"
    LOGGER_PATH: str = "logs/app.log"
    METRICS_UPDATE_INTERVAL: int = 30
    APP_NAME: str = "FastAPI Orders Service"
    USERS_SERVICE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
