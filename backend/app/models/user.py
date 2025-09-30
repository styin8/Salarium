from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=64, unique=True)
    password_hash = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"