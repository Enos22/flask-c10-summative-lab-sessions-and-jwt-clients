from marshmallow import Schema, fields, validate
from models.medication_schedule import DAY_ORDER


class ScheduleSchema(Schema):
    id = fields.Int(dump_only=True)
    medication_id = fields.Int(required=True)
    reminder_time = fields.Time(required=True, format="%H:%M")
    days_of_week = fields.List(
        fields.Str(validate=validate.OneOf(DAY_ORDER)),
        required=True,
        attribute="days_list",
        validate=validate.Length(min=1, error="Select at least one day."),
    )
    is_active = fields.Bool(load_default=True)


schedule_schema = ScheduleSchema()
schedules_schema = ScheduleSchema(many=True)
