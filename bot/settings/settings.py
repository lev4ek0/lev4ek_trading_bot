from dotenv import load_dotenv
from pydantic import BaseSettings, Field, SecretStr

load_dotenv()


class BotSettings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="TELEGRAM_API_TOKEN")
    WEBHOOK_HOST: str
    WEBHOOK_PATH: str
    WEBHOOK_URL: str
    IS_POLLING: bool = False
    WEBAPP_HOST: str
    WEBAPP_PORT: int

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class SQLAlchemyOrmSettings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


bot_settings = BotSettings()
sqlalchemy_orm_settings = SQLAlchemyOrmSettings()
redis_settings = RedisSettings()

SQLALCHEMY_ORM_CONFIG = {
    "url": f"postgresql+asyncpg://{sqlalchemy_orm_settings.POSTGRES_USER}:"
    f"{sqlalchemy_orm_settings.POSTGRES_PASSWORD}@"
    f"{sqlalchemy_orm_settings.POSTGRES_HOST}:"
    f"{sqlalchemy_orm_settings.POSTGRES_PORT}/"
    f"{sqlalchemy_orm_settings.POSTGRES_DB}",
    "echo": True,
}
