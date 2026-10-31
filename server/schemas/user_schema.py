#Enos
from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.int()
    username = fields.String()
