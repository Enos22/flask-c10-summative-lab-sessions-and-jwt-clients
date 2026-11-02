#benson
from flask import Blueprint, request, jsonify, session

from marshmallow import ValidationError

from extensions import db
from models.medication import Medication
from schemas.medication_schema import (
    medication_schema,
    medications_schema
)

medications_bp = Blueprint(
    "medications",
    __name__,
    url_prefix="/api/medications"
)


# CREATE: Add a medication
@medications_bp.route("/addmedication", methods=["POST"])
def add_medication():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        medication_data = medication_schema.load(data)

        medication = Medication(
            name=medication_data["name"],
            dosage=medication_data["dosage"],
            instructions=medication_data.get("instructions"),
            start_date=medication_data["start_date"],
            end_date=medication_data.get("end_date"),
            user_id=user_id
        )

        db.session.add(medication)
        db.session.commit()

        return jsonify({
            "message": "Medication added successfully",
            "medication": medication_schema.dump(medication)
        }), 201

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not add medication"}), 500


# READ: View all medications
@medications_bp.route("/getmedications", methods=["GET"])
def get_medications():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    medications = Medication.query.all()
    print(medications)
    return jsonify({
        "medications": medications_schema.dump(medications)
    }), 200


# READ: View one medication
@medications_bp.route("/getmedication/<int:medication_id>", methods=["GET"])
def get_medication(medication_id):

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    medication = Medication.query.filter_by(
        id=medication_id,
        user_id=user_id
    ).first()

    if medication is None:
        return jsonify({"error": "Medication not found"}), 404

    return jsonify({
        "medication": medication_schema.dump(medication)
    }), 200


# UPDATE: Update medication
@medications_bp.route("/update/<int:medication_id>", methods=["PATCH"])
def update_medication(medication_id):

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    medication = Medication.query.filter_by(
        id=medication_id,
        user_id=user_id
    ).first()

    if medication is None:
        return jsonify({"error": "Medication not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        updated_data = medication_schema.load(
            data,
            partial=True
        )

        new_start_date = updated_data.get(
            "start_date", medication.start_date
        )

        new_end_date = updated_data.get(
            "end_date", medication.end_date
        )

        if new_end_date and new_end_date < new_start_date:
            return jsonify({
                "error": "End date cannot be before start date"
            }), 400

        for field, value in updated_data.items():
            setattr(medication, field, value)

        db.session.commit()

        return jsonify({
            "message": "Medication updated successfully",
            "medication": medication_schema.dump(medication)
        }), 200

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Could not update medication"}), 500


# DELETE: Delete medication
@medications_bp.route("/delete/<int:medication_id>", methods=["DELETE"])
def delete_medication(medication_id):

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Please log in first"}), 401

    medication = Medication.query.filter_by(
        id=medication_id,
        user_id=user_id
    ).first()

    if medication is None:
        return jsonify({"error": "Medication not found"}), 404

    try:
        db.session.delete(medication)
        db.session.commit()

        return jsonify({
            "message": "Medication deleted successfully"
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "error": "Could not delete medication"
        }), 500
