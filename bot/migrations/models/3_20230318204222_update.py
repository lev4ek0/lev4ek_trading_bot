from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uid_user_tinkoff_b150fa" ON "user" ("tinkoff_account_id");
        CREATE UNIQUE INDEX "uid_user_tinkoff_54047f" ON "user" ("tinkoff_api_key");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_user_tinkoff_54047f";
        DROP INDEX "idx_user_tinkoff_b150fa";"""
