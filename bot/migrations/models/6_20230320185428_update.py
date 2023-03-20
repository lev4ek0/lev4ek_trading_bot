from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" RENAME COLUMN "notifications" TO "is_notifications";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" RENAME COLUMN "is_notifications" TO "notifications";"""
