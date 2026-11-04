"""Reminder logic for MediReminder.

Owner: Fiona (Reminders & Reports)

Answers "which medications does this user need to take soon?".

How it fits the team's models:
    MedicationSchedule.reminder_time  time of day the user takes the medicine
    MedicationSchedule.days           "mon,wed,fri" (empty means every day)
    MedicationSchedule.is_active      inactive schedules are ignored
    Medication.start_date/end_date    schedule only runs inside this range
    Dose.scheduled_for                naive UTC datetime of one occurrence
    Dose.status                       pending / taken / missed

TIME ZONES
    Doses are stored as naive UTC (see models/dose.py). A schedule's
    reminder_time is what the user sees on their clock, so it is treated as
    LOCAL time and converted to UTC. Local time defaults to Nairobi (UTC+3).
    Change it with the environment variable LOCAL_UTC_OFFSET_HOURS.
"""
import os
from datetime import date, datetime, timedelta, timezone

from extensions import db
from models.dose import PENDING, Dose
from models.medication import Medication
from models.medication_schedule import MedicationSchedule

LOCAL_OFFSET = timedelta(hours=int(os.environ.get("LOCAL_UTC_OFFSET_HOURS", "3")))
DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]  # Monday = 0


# --------------------------------------------------------------------------
# Time helpers (shared with adherence_service)
# --------------------------------------------------------------------------
def utc_now():
    """Current time as a naive UTC datetime (the format the database uses)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_local(dt_utc):
    return dt_utc + LOCAL_OFFSET


def to_utc(dt_local):
    return dt_local - LOCAL_OFFSET


def local_today(now=None):
    return to_local(now or utc_now()).date()


def iso_utc(dt):
    """ISO string with a trailing Z so JavaScript shows it in local time."""
    return dt.isoformat() + "Z" if dt else None


def local_range_to_utc(start_date, end_date):
    """Inclusive LOCAL dates -> [start_utc, end_utc) naive UTC datetimes."""
    start = to_utc(datetime.combine(start_date, datetime.min.time()))
    end = to_utc(datetime.combine(end_date + timedelta(days=1), datetime.min.time()))
    return start, end


# --------------------------------------------------------------------------
# Schedule helpers
# --------------------------------------------------------------------------
def parse_days(value):
    """Turn the schedule's days into a set of weekday numbers (Monday = 0).

    Accepts "mon,wed", a list of names, or numbers 0-6. Empty means every day.
    """
    if value is None or value == "" or value == []:
        return set(range(7))
    if isinstance(value, str):
        value = value.replace(";", ",").split(",")

    days = set()
    for item in value:
        item = str(item).strip().lower()
        if not item:
            continue
        if item.isdigit():
            days.add(int(item) % 7)
        elif item[:3] in DAY_NAMES:
            days.add(DAY_NAMES.index(item[:3]))
    return days or set(range(7))


def runs_on(schedule, medication, day):
    """True if this schedule produces a dose on the given LOCAL date."""
    if not schedule.is_active:
        return False
    if medication.start_date and day < medication.start_date:
        return False
    if medication.end_date and day > medication.end_date:
        return False
    return day.weekday() in parse_days(schedule.days)


def occurrence_utc(schedule, day):
    """The UTC moment a schedule fires on a LOCAL date."""
    return to_utc(datetime.combine(day, schedule.reminder_time))


def user_schedules(user_id):
    """Active (schedule, medication) pairs owned by the user."""
    return (
        db.session.query(MedicationSchedule, Medication)
        .join(Medication, MedicationSchedule.medication_id == Medication.id)
        .filter(Medication.user_id == user_id, MedicationSchedule.is_active.is_(True))
        .all()
    )


def find_dose(schedule_id, when_utc):
    return Dose.query.filter_by(schedule_id=schedule_id, scheduled_for=when_utc).first()


def _reminder_dict(schedule, medication, when, dose, now):
    minutes_until = int((when - now).total_seconds() // 60)
    return {
        "schedule_id": schedule.id,
        "dose_id": dose.id if dose else None,
        "medication_id": medication.id,
        "medication_name": medication.name,
        "dosage": medication.dosage,
        "scheduled_time": iso_utc(when),
        "minutes_until": minutes_until,
        "status": "overdue" if minutes_until < 0 else "upcoming",
    }


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def get_reminders(user_id, window_minutes=60, overdue_minutes=60, now=None):
    """Pending doses from `overdue_minutes` ago up to `window_minutes` ahead.

    Doses already taken or marked missed are left out.
    """
    now = now or utc_now()
    start = now - timedelta(minutes=overdue_minutes)
    end = now + timedelta(minutes=window_minutes)
    local_days = {to_local(start).date(), to_local(now).date(), to_local(end).date()}

    reminders = []
    for schedule, medication in user_schedules(user_id):
        for day in local_days:
            if not runs_on(schedule, medication, day):
                continue
            when = occurrence_utc(schedule, day)
            if not (start <= when <= end):
                continue
            dose = find_dose(schedule.id, when)
            if dose and dose.status != PENDING:
                continue
            reminders.append(_reminder_dict(schedule, medication, when, dose, now))

    reminders.sort(key=lambda r: r["scheduled_time"])
    return reminders


def get_upcoming_reminders(user_id, window_minutes=60, now=None):
    """Doses that have not happened yet (next `window_minutes`)."""
    return [r for r in get_reminders(user_id, window_minutes, 0, now)
            if r["minutes_until"] >= 0]


def get_due_reminders(user_id, overdue_minutes=60, now=None):
    """Doses due now or overdue and still unmarked."""
    return [r for r in get_reminders(user_id, 0, overdue_minutes, now)
            if r["minutes_until"] <= 0]


def generate_doses_for_date(user_id, day=None, commit=True):
    """Create 'pending' Dose rows for every schedule running on a LOCAL date.

    Safe to run twice: existing rows are skipped (the Dose table also has a
    unique constraint on schedule + time). Returns how many were created.
    """
    day = day or local_today()
    created = 0
    for schedule, medication in user_schedules(user_id):
        if not runs_on(schedule, medication, day):
            continue
        when = occurrence_utc(schedule, day)
        if find_dose(schedule.id, when):
            continue
        db.session.add(Dose(schedule_id=schedule.id, scheduled_for=when, status=PENDING))
        created += 1

    if commit and created:
        db.session.commit()
    return created