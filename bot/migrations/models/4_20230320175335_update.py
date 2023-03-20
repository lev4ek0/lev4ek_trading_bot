from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "history" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "command" VARCHAR(255) NOT NULL,
    "chat_id" BIGINT NOT NULL REFERENCES "chat" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "history";"""
