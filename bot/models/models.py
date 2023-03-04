from tortoise import Model
from tortoise.fields import IntField, CharField, FloatField


class Share(Model):
    id = IntField(pk=True)
    name = CharField(max_length=255)
    figi = CharField(max_length=32)
    proportion = FloatField(max_length=32)
