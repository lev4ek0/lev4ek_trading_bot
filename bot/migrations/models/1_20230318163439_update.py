from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "chat" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(32) NOT NULL
);;
        ALTER TABLE "share" ADD "user_id" BIGINT NOT NULL;
        CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(255) NOT NULL,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "active_conversation" BOOL NOT NULL  DEFAULT True,
    "banned" BOOL NOT NULL  DEFAULT False
);;
        ALTER TABLE "share" ADD CONSTRAINT "fk_share_user_2eb95678" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "share" DROP CONSTRAINT "fk_share_user_2eb95678";
        ALTER TABLE "share" DROP COLUMN "user_id";
        DROP TABLE IF EXISTS "chat";
        DROP TABLE IF EXISTS "user";"""
