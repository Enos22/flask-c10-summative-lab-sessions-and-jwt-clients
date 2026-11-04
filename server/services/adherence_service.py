#Fiona
"""Adherence calculations for MediReminder.

Owner: Fiona (Reminders & Reports)

This module reads Dose records (owned by the Dose Tracking module) and turns
them into numbers: how many doses were taken, missed or are still pending,
and what percentage of resolved doses were taken.
        
"""
from datetime import date, datetime, timedelta

from extensions import db
from models.dose import Dose
from models.medication import Medication
from models.medication_schedule import MedicationSchedule

# A pending dose becomes "missed" this many minutes after its scheduled time.
GRACE_MINUTES = 60


# --------------------------------------------------------------------------
# Queries and helpers
# --------------------------------------------------------------------------
def user_doses_query(user_id):
    """Base query: every (Dose, Schedule, Medication) row owned by a user."""
    return (
        db.session.query(Dose, MedicationSchedule, Medication)
        .join(MedicationSchedule, Dose.schedule_id == MedicationSchedule.id)
        .join(Medication, MedicationSchedule.medication_id == Medication.id)
        .filter(Medication.user_id == user_id)
    )


def effective_status(dose, now=None, grace_minutes=GRACE_MINUTES):
    """Return 'taken', 'missed' or 'pending' for a dose.

    A dose still marked 'pending' whose grace period has passed counts as
    'missed', so adherence stays correct even if nobody marked it.
    """
    now = now or datetime.now()
    status = (dose.status or "pending").lower()
    if status == "pending":
        #changed dose.scheduled_for to dose.scheduled_for
        if dose.scheduled_for + timedelta(minutes=grace_minutes) < now:
            return "missed"
    return status


def dose_to_dict(dose, schedule, medication, now=None):
    """Plain dict for JSON responses (no Marshmallow needed for reports)."""
    taken_at = getattr(dose, "taken_at", None)
    return {
        "dose_id": dose.id,
        "schedule_id": schedule.id,
        "medication_id": medication.id,
        "medication_name": medication.name,
        "dosage": medication.dosage,
                #changed dose.scheduled_for to dose.scheduled_for
        "scheduled_time": dose.scheduled_for.isoformat(),
        "status": effective_status(dose, now),
        "recorded_status": dose.status,
        "taken_at": taken_at.isoformat() if taken_at else None,
    }


def _day_bounds(start_date, end_date):
    """Inclusive date range -> [start_dt, end_dt) datetimes."""
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
    return start_dt, end_dt


def fetch_dose_dicts(user_id, start_date, end_date, now=None):
    """All of a user's doses between two dates (inclusive), oldest first."""
    now = now or datetime.now()
    start_dt, end_dt = _day_bounds(start_date, end_date)
    rows = (
        user_doses_query(user_id)
        .filter(Dose.scheduled_for >= start_dt, Dose.scheduled_for < end_dt)
        .order_by(Dose.scheduled_for)
        .all()
    )
    return [dose_to_dict(d, s, m, now) for d, s, m in rows]


# --------------------------------------------------------------------------
# Calculations
# --------------------------------------------------------------------------
def summarize(statuses):
    """Count statuses and compute the adherence rate.

    adherence_rate = taken / (taken + missed) * 100
    Pending doses are not counted yet, because they are still undecided.
    Returns None for the rate when nothing has been resolved.
    """
    statuses = list(statuses)
    taken = statuses.count("taken")
    missed = statuses.count("missed")
    pending = statuses.count("pending")
    resolved = taken + missed
    rate = round(taken / resolved * 100, 1) if resolved else None
    return {
        "total": len(statuses),
        "taken": taken,
        "missed": missed,
        "pending": pending,
        "adherence_rate": rate,
    }


def calculate_adherence(user_id, start_date, end_date, now=None):
    """Overall adherence plus a per-medication breakdown for a date range."""
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
    """One summary per day (days with no doses are included with zeros)."""
    doses = fetch_dose_dicts(user_id, start_date, end_date, now)

    per_day = {}
    for d in doses:
        day = d["scheduled_time"][:10]  # 'YYYY-MM-DD'
        per_day.setdefault(day, []).append(d["status"])

    history = []
    day = start_date
    while day <= end_date:
        key = day.isoformat()
        history.append({"date": key, **summarize(per_day.get(key, []))})
        day += timedelta(days=1)
    return history