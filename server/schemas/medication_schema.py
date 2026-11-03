#benson

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class MedicationSchema(Schema):

    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    dosage = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

    instructions = fields.Str(
        allow_none=True
    )

    start_date = fields.Date(
        required=True
    )

    end_date = fields.Date(
        allow_none=True
    )

    user_id = fields.Int(dump_only=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise ValidationError(
                "End date cannot be before start date."
            )

medication_schema = MedicationSchema()
medications_schema = MedicationSchema(many=True)