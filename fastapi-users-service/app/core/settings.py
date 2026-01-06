from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    LOGGER_NAME: str = "fastapi-users-service"
    LOGGER_PATH: str = "logs/app.log"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Configuration
    PASSWORD_MIN_LENGTH: int = 4
    BCRYPT_ROUNDS: int = 12

    class Config:
        env_file = ".env"

    class Config:
        env_file = ".env"


settings = Settings()
