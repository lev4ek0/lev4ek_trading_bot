from pydantic import BaseSettings, Field, SecretStr
from dotenv import load_dotenv

load_dotenv()


class TinkoffSettings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="TINKOFF_API_TOKEN")
    ACCOUNT_ID: str

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class BotSettings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="TELEGRAM_API_TOKEN")
    WEBHOOK_HOST: str
    WEBHOOK_PATH: str
    WEBHOOK_URL: str
    IS_POLLING: bool = False

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


tinkoff_settings = TinkoffSettings()
bot_settings = BotSettings()
tortoise_orm_settings = TortoiseOrmSettings()

TORTOISE_ORM_CONFIG = {
    "connections": {
        "default": {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': tortoise_orm_settings.POSTGRES_HOST,
                'port': tortoise_orm_settings.POSTGRES_PORT,
                'user': tortoise_orm_settings.POSTGRES_USER,
                'password': tortoise_orm_settings.POSTGRES_PASSWORD,
                'database': tortoise_orm_settings.POSTGRES_DB,
            }
        }
    },
    "apps": {
        "models": {
            "models": ["models.base", "aerich.models"],
            "default_connection": "default",
        },
    },
}
