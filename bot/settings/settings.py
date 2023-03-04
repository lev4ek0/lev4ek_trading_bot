from pydantic import BaseSettings, Field, SecretStr
from dotenv import load_dotenv

load_dotenv()


class TinkoffSettings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="TINKOFF_API_TOKEN")
    ACCOUNT_ID: str

    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'


class BotSettings(BaseSettings):
    TOKEN: SecretStr = Field(..., env="TELEGRAM_API_TOKEN")
    WEBHOOK_HOST: str
    WEBHOOK_PATH: str
    WEBHOOK_URL: str
    IS_POLLING: bool = False

    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'


tinkoff_settings = TinkoffSettings()
bot_settings = BotSettings()
