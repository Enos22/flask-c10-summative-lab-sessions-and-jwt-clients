from datetime import date, datetime, time, timedelta, timezone

from flask import Blueprint, jsonify, request, session  # type: ignore[reportMissingImports]
from marshmallow import ValidationError  # type: ignore[reportMissingImports]

from extensions import db
from models.dose import DOSE_STATUSES, MISSED, TAKEN, Dose
from models.medication import Medication
from models.medication_schedule import MedicationSchedule
from schemas.dose_schema import DoseSchema, DoseTakenSchema

dose_bp = Blueprint("doses", __name__, url_prefix="/api/doses")

dose_schema = DoseSchema()
doses_schema = DoseSchema(many=True)
taken_schema = DoseTakenSchema()


def _user_id():
    # ONE place to change if Enos's auth stores the user differently.
    return session.get("user_id")


@dose_bp.before_request
def require_login():
    if _user_id() is None:
        return jsonify({"error": "Authentication required."}), 401


def _user_doses():
    return (
        Dose.query.join(MedicationSchedule, Dose.schedule_id == MedicationSchedule.id)
        .join(Medication, MedicationSchedule.medication_id == Medication.id)
        .filter(Medication.user_id == _user_id())
    )


def _get_dose(dose_id):
    # Another user's dose looks identical to a missing one (404, never 403).
    return _user_doses().filter(Dose.id == dose_id).first()


@dose_bp.get("")
def list_doses():
    query = _user_doses()

    day = request.args.get("date")
    if day:
        try:
            start = datetime.combine(date.fromisoformat(day), time.min)
        except ValueError:
            return jsonify({"error": "date must be YYYY-MM-DD."}), 400
        query = query.filter(
            Dose.scheduled_for >= start,
            Dose.scheduled_for < start + timedelta(days=1),
        )

    status = request.args.get("status")
    if status:
        if status not in DOSE_STATUSES:
            return jsonify({"error": f"status must be one of {list(DOSE_STATUSES)}."}), 400
        query = query.filter(Dose.status == status)

    doses = query.order_by(Dose.scheduled_for.asc()).all()
    return jsonify(doses_schema.dump(doses)), 200


@dose_bp.get("/<int:dose_id>")
def get_dose(dose_id):
    dose = _get_dose(dose_id)
    if dose is None:
        return jsonify({"error": "Dose not found."}), 404
    return jsonify(dose_schema.dump(dose)), 200


@dose_bp.patch("/<int:dose_id>/taken")
def mark_taken(dose_id):
    dose = _get_dose(dose_id)
    if dose is None:
        return jsonify({"error": "Dose not found."}), 404

    try:
        data = taken_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    taken_at = data.get("taken_at") or datetime.now(timezone.utc)
    if taken_at.tzinfo is not None:
        taken_at = taken_at.astimezone(timezone.utc).replace(tzinfo=None)

    dose.status = TAKEN
    dose.taken_at = taken_at
    db.session.commit()
    return jsonify(dose_schema.dump(dose)), 200


@dose_bp.patch("/<int:dose_id>/missed")
def mark_missed(dose_id):
    dose = _get_dose(dose_id)
    if dose is None:
        return jsonify({"error": "Dose not found."}), 404

    dose.status = MISSED
    dose.taken_at = None
    db.session.commit()
    return jsonify(dose_schema.dump(dose)), 200