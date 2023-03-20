from tortoise import Model
from tortoise.fields import (
    BooleanField,
    BigIntField,
    CharField,
    FloatField,
    ForeignKeyField,
    ForeignKeyRelation,
    CASCADE,
    ReverseRelation,
    IntField,
)


class User(Model):
    id = BigIntField(pk=True, index=True, unique=True)
    full_name = CharField(max_length=255)
    is_superuser = BooleanField(default=False)
    active_conversation = BooleanField(default=True)
    banned = BooleanField(default=False)
    tinkoff_api_key = CharField(max_length=255, unique=True, null=True)
    tinkoff_account_id = CharField(max_length=255, unique=True, null=True)
    is_notifications = BooleanField(default=True)

    histories: ReverseRelation["History"]
    shares: ReverseRelation["Share"]

    @property
    def accounts(self):
        return {"Tinkoff": [self.tinkoff_account_id]} if self.can_trade else {}

    @property
    def can_trade(self):
        return bool(self.tinkoff_api_key and self.tinkoff_account_id)

    def __str__(self):
        return self.full_name


class Share(Model):
    id = IntField(pk=True, index=True, unique=True)
    name = CharField(max_length=255)
    figi = CharField(max_length=32)
    proportion = FloatField()
    user: ForeignKeyRelation[User] = ForeignKeyField(
        model_name="models.User",
        related_name="shares",
        on_delete=CASCADE,
    )

    def __str__(self):
        return f"{self.name}: {self.proportion * 100:.2f}"

    class Meta:
        unique_together = ("figi", "user")


class Chat(Model):
    id = BigIntField(pk=True, index=True)
    type = CharField(max_length=32)

    histories: ReverseRelation["History"]

    def __str__(self):
        return f"{self.type}:{self.id}"


class History(Model):
    id = IntField(pk=True, index=True, unique=True)
    command = CharField(max_length=255)
    user: ForeignKeyRelation[User] = ForeignKeyField(
        model_name="models.User",
        related_name="histories",
        on_delete=CASCADE,
    )
    chat: ForeignKeyRelation[Chat] = ForeignKeyField(
        model_name="models.Chat",
        related_name="histories",
        on_delete=CASCADE,
    )

    def __str__(self):
        return f"{self.user}: {self.command}"
