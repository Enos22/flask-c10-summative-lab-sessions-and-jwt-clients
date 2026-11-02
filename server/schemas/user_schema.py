from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=20, error="Username too Short!"),
            validate.Regexp(r'^[A-Za-z0-9_]+$', error="Only letters, numbers and _ allowed!")
        ]
    )

user_schema = UserSchema()
users_schema = UserSchema(many=True)
