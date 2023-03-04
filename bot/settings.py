from typing import Optional

from pydantic import BaseSettings, Field, SecretStr
from dotenv import load_dotenv

load_dotenv()


class TinkoffSettings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="TINKOFF_API_TOKEN")
    ACCOUNT_ID: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


class BotSettings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="TELEGRAM_API_TOKEN")
    WEBHOOK_HOST: str = 'bot.lev4ek.ru'
    WEBHOOK_PATH: Optional[str] = '/api/bot'
    WEBHOOK_URL: str = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


tinkoff_settings = TinkoffSettings()
bot_settings = BotSettings()
