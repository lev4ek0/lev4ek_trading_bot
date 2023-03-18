from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "tinkoff_account_id" VARCHAR(255);
        ALTER TABLE "user" ADD "tinkoff_api_key" VARCHAR(255);
        CREATE UNIQUE INDEX "uid_share_figi_6f1faa" ON "share" ("figi", "user_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_share_figi_6f1faa";
        ALTER TABLE "user" DROP COLUMN "tinkoff_account_id";
        ALTER TABLE "user" DROP COLUMN "tinkoff_api_key";"""
