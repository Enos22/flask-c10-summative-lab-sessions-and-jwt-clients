"""Adherence calculations for MediReminder.

Owner: Fiona (Reminders & Reports)

Reads Dose rows (Dose Tracking module) and turns them into numbers: how many
doses were taken, missed or are pending, and what percent were taken.

Dates passed in and returned are LOCAL dates (Nairobi by default). The
database stores UTC, and the conversion happens in reminder_service.
"""
from datetime import timedelta

from extensions import db
from models.dose import MISSED, PENDING, TAKEN, Dose
from models.medication import Medication
from models.medication_schedule import MedicationSchedule
from services.reminder_service import (
    iso_utc,
    local_range_to_utc,
    to_local,
    utc_now,
)

# A pending dose counts as missed this many minutes after its scheduled time.
GRACE_MINUTES = 60


def user_doses_query(user_id):
    """Every (Dose, Schedule, Medication) row owned by a user."""
    return (
        db.session.query(Dose, MedicationSchedule, Medication)
        .join(MedicationSchedule, Dose.schedule_id == MedicationSchedule.id)
        .join(Medication, MedicationSchedule.medication_id == Medication.id)
        .filter(Medication.user_id == user_id)
    )


def effective_status(dose, now=None, grace_minutes=GRACE_MINUTES):
    """'taken', 'missed' or 'pending'. Old unmarked pending doses become missed."""
    now = now or utc_now()
    if dose.status == PENDING:
        if dose.scheduled_for + timedelta(minutes=grace_minutes) < now:
            return MISSED
    return dose.status


def dose_to_dict(dose, schedule, medication, now=None):
    return {
        "dose_id": dose.id,
        "schedule_id": schedule.id,
        "medication_id": medication.id,
        "medication_name": medication.name,
        "dosage": medication.dosage,
        "scheduled_time": iso_utc(dose.scheduled_for),
        "date": to_local(dose.scheduled_for).date().isoformat(),  # local day
        "status": effective_status(dose, now),
        "recorded_status": dose.status,
        "taken_at": iso_utc(dose.taken_at),
    }


def fetch_dose_dicts(user_id, start_date, end_date, now=None):
    """A user's doses between two LOCAL dates (inclusive), oldest first."""
    now = now or utc_now()
    start_utc, end_utc = local_range_to_utc(start_date, end_date)
    rows = (
        user_doses_query(user_id)
        .filter(Dose.scheduled_for >= start_utc, Dose.scheduled_for < end_utc)
        .order_by(Dose.scheduled_for)
        .all()
    )
    return [dose_to_dict(d, s, m, now) for d, s, m in rows]


def summarize(statuses):
    """Counts plus adherence_rate = taken / (taken + missed) * 100.

    Pending doses are not counted yet. The rate is None if nothing is resolved.
    """
    statuses = list(statuses)
    taken = statuses.count(TAKEN)
    missed = statuses.count(MISSED)
    pending = statuses.count(PENDING)
    resolved = taken + missed
    return {
        "total": len(statuses),
        "taken": taken,
        "missed": missed,
        "pending": pending,
        "adherence_rate": round(taken / resolved * 100, 1) if resolved else None,
    }


def calculate_adherence(user_id, start_date, end_date, now=None):
    """Overall adherence plus a per-medication breakdown."""
    doses = fetch_dose_dicts(user_id, start_date, end_date, now)

    by_med = {}
    for d in doses:
        by_med.setdefault(
            d["medication_id"], {"name": d["medication_name"], "statuses": []}
        )["statuses"].append(d["status"])

    return {
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        **summarize(d["status"] for d in doses),
        "by_medication": [
            {"medication_id": mid, "medication_name": info["name"],
             **summarize(info["statuses"])}
            for mid, info in by_med.items()
        ],
    }


def daily_history(user_id, start_date, end_date, now=None):
    """One summary per local day, including days with no doses."""
    doses = fetch_dose_dicts(user_id, start_date, end_date, now)

    per_day = {}
    for d in doses:
        per_day.setdefault(d["date"], []).append(d["status"])

    history, day = [], start_date
    while day <= end_date:
        key = day.isoformat()
        history.append({"date": key, **summarize(per_day.get(key, []))})
        day += timedelta(days=1)
    return history