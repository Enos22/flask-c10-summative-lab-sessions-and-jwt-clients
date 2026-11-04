from functools import wraps

from flask import Blueprint, jsonify, request, session
from marshmallow import ValidationError

from extensions import db
from models.medication import Medication
from schemas.medication_schema import medication_schema, medications_schema

medications_bp = Blueprint(
    "medications", __name__, url_prefix="/api/medications"
)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return jsonify(error="Please log in first"), 401
        return view(*args, **kwargs)
    return wrapper


def get_owned_medication(medication_id):
    return Medication.query.filter_by(
        id=medication_id, user_id=session["user_id"]
    ).first()


@medications_bp.post("/addmedication")
@login_required
def add_medication():
    try:
        data = medication_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify(errors=err.messages), 400

    medication = Medication(
        name=data["name"],
        dosage=data["dosage"],
        instructions=data.get("instructions"),
        start_date=data["start_date"],
        end_date=data.get("end_date"),
        user_id=session["user_id"],
    )
    db.session.add(medication)
    db.session.commit()
    return jsonify(
        message="Medication added successfully",
        medication=medication_schema.dump(medication),
    ), 201


@medications_bp.get("/getmedications")
@login_required
def get_medications():
    medications = Medication.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Medication.id.desc()).all()
    return jsonify(medications=medications_schema.dump(medications)), 200


@medications_bp.get("/getmedication/<int:medication_id>")
@login_required
def get_medication(medication_id):
    medication = get_owned_medication(medication_id)
    if medication is None:
        return jsonify(error="Medication not found"), 404
    return jsonify(medication=medication_schema.dump(medication)), 200


@medications_bp.patch("/update/<int:medication_id>")
@login_required
def update_medication(medication_id):
    medication = get_owned_medication(medication_id)
    if medication is None:
        return jsonify(error="Medication not found"), 404

    try:
        data = medication_schema.load(
            request.get_json(silent=True) or {}, partial=True
        )
    except ValidationError as err:
        return jsonify(errors=err.messages), 400

    start_date = data.get("start_date", medication.start_date)
    end_date = data.get("end_date", medication.end_date)
    if end_date and end_date < start_date:
        return jsonify(error="End date cannot be before start date"), 400

    for key, value in data.items():
        setattr(medication, key, value)
    db.session.commit()
    return jsonify(
        message="Medication updated successfully",
        medication=medication_schema.dump(medication),
    ), 200


@medications_bp.delete("/delete/<int:medication_id>")
@login_required
def delete_medication(medication_id):
    medication = get_owned_medication(medication_id)
    if medication is None:
        return jsonify(error="Medication not found"), 404
    db.session.delete(medication)
    db.session.commit()
    return jsonify(message="Medication deleted successfully"), 200
