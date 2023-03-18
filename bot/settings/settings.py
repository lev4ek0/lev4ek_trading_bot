from pydantic import BaseSettings, Field, SecretStr
from dotenv import load_dotenv

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


class TortoiseOrmSettings(BaseSettings):
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
tortoise_orm_settings = TortoiseOrmSettings()
redis_settings = RedisSettings()

TORTOISE_ORM_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": tortoise_orm_settings.POSTGRES_HOST,
                "port": tortoise_orm_settings.POSTGRES_PORT,
                "user": tortoise_orm_settings.POSTGRES_USER,
                "password": tortoise_orm_settings.POSTGRES_PASSWORD,
                "database": tortoise_orm_settings.POSTGRES_DB,
            },
        }
    },
    "apps": {
        "models": {
            "models": ["models.base", "aerich.models"],
            "default_connection": "default",
        },
    },
}
