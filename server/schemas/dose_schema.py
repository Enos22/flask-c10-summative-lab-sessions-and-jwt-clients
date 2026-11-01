from datetime import datetime, timedelta, timezone

from marshmallow import Schema, ValidationError, fields, validates  # type: ignore[import-not-found]


class DoseSchema(Schema):
    """Output only: what the frontend receives."""

    id = fields.Int(dump_only=True)
    schedule_id = fields.Int(dump_only=True)
    scheduled_for = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    taken_at = fields.DateTime(dump_only=True, allow_none=True)


class DoseTakenSchema(Schema):
    """Input for PATCH /taken. taken_at is optional and defaults to now."""

    taken_at = fields.DateTime(load_default=None, allow_none=True)

    @validates("taken_at")
    def validate_taken_at(self, value, **kwargs):
        if value is None:
            return
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if value > now + timedelta(minutes=1):
            raise ValidationError("taken_at cannot be in the future.")