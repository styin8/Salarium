from tortoise import fields
from tortoise.models import Model


class Person(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64)
    note = fields.CharField(max_length=255, null=True)
    user = fields.ForeignKeyField("models.User", related_name="persons")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "persons"