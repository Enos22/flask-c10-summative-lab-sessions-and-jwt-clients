from functools import wraps

from flask import Blueprint, jsonify, request, session
from marshmallow import ValidationError

from extensions import db
from models.medication import Medication
from models.medication_schedule import MedicationSchedule
from schemas.schedule_schema import schedule_schema, schedules_schema

schedules_bp = Blueprint("schedules", __name__, url_prefix="/api/schedules")
MAX_PER_PAGE = 50


def current_user_id():
    return session.get("user_id")


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user_id() is None:
            return jsonify(error="Authentication required."), 401
        return view(*args, **kwargs)
    return wrapper


def get_owned_schedule(schedule_id):
    return (
        MedicationSchedule.query.join(Medication)
        .filter(
            MedicationSchedule.id == schedule_id,
            Medication.user_id == current_user_id(),
        )
        .first()
    )


def owns_medication(medication_id):
    return Medication.query.filter_by(
        id=medication_id, user_id=current_user_id()
    ).first() is not None


@schedules_bp.get("")
@login_required
def list_schedules():
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 10, type=int), 1), MAX_PER_PAGE)
    query = (
        MedicationSchedule.query.join(Medication)
        .filter(Medication.user_id == current_user_id())
        .order_by(MedicationSchedule.id)
    )
    medication_id = request.args.get("medication_id", type=int)
    if medication_id is not None:
        query = query.filter(MedicationSchedule.medication_id == medication_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        items=schedules_schema.dump(pagination.items),
        page=pagination.page,
        per_page=pagination.per_page,
        total=pagination.total,
        pages=pagination.pages,
    ), 200


@schedules_bp.get("/<int:schedule_id>")
@login_required
def get_schedule(schedule_id):
    schedule = get_owned_schedule(schedule_id)
    if schedule is None:
        return jsonify(error="Schedule not found."), 404
    return jsonify(schedule_schema.dump(schedule)), 200


@schedules_bp.post("")
@login_required
def create_schedule():
    try:
        data = schedule_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify(errors=err.messages), 422

    if not owns_medication(data["medication_id"]):
        return jsonify(error="Medication not found."), 404

    schedule = MedicationSchedule(
        medication_id=data["medication_id"],
        reminder_time=data["reminder_time"],
        days_list=data["days_list"],
        is_active=data.get("is_active", True),
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify(schedule_schema.dump(schedule)), 201


@schedules_bp.route("/<int:schedule_id>", methods=["PATCH", "PUT"])
@login_required
def update_schedule(schedule_id):
    schedule = get_owned_schedule(schedule_id)
    if schedule is None:
        return jsonify(error="Schedule not found."), 404

    try:
        data = schedule_schema.load(
            request.get_json(silent=True) or {}, partial=True
        )
    except ValidationError as err:
        return jsonify(errors=err.messages), 422

    if "medication_id" in data and not owns_medication(data["medication_id"]):
        return jsonify(error="Medication not found."), 404

    for field, value in data.items():
        setattr(schedule, field, value)
    db.session.commit()
    return jsonify(schedule_schema.dump(schedule)), 200


@schedules_bp.delete("/<int:schedule_id>")
@login_required
def delete_schedule(schedule_id):
    schedule = get_owned_schedule(schedule_id)
    if schedule is None:
        return jsonify(error="Schedule not found."), 404
    db.session.delete(schedule)
    db.session.commit()
    return "", 204
