from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(
        required=True
        valiadate=[
            valiadte.Length(min=3, max=20, error="Username too Short!"),
            validate.Regex(r'^[a-zA-z0-9_]+$', error="Only letters, numbers and _ allowed!")
        ]
    )
    class Meta:
        exclude =('_password_hash',)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
