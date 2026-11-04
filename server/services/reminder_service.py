#Fiona
"""Reminder logic for MediReminder.

Owner: Fiona (Reminders & Reports)

Answers the question "which medications does this user need to take soon?"
It works from the MedicationSchedule rows (time of day + days of the week)
and checks the Dose table to skip anything already taken.

Assumed model fields (agree these with the team before merging):
    MedicationSchedule: id, medication_id, time (datetime.time), days_of_week
    Dose:               id, schedule_id, scheduled_time, status, taken_at
"""
from datetime import date, datetime, timedelta

from extensions import db
from models.dose import Dose
from models.medication import Medication
from models.medication_schedule import MedicationSchedule

DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]  # Monday = 0


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def parse_days(value):
    """Turn whatever the schedule stores into a set of weekday numbers.

    Accepts: None/empty (every day), a list or comma-separated string, of
    names ("Mon", "monday") or numbers (0-6, Monday = 0).
    """
    if value is None or value == "" or value == []:
        return set(range(7))

    if isinstance(value, str):
        value = [part for part in value.replace(";", ",").split(",")]

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


def occurs_on(schedule, day):
    """True if the schedule runs on the given date."""
    #corrected logic from days of week to days
    return day.weekday() in parse_days(schedule.days)


def occurrence_datetime(schedule, day):
    """The exact datetime a schedule fires on a given date."""
    #corrcted frm schedule.time to schedule.reminder_time for clarity
    return datetime.combine(day, schedule.reminder_time)


def user_schedules(user_id):
    """All (schedule, medication) pairs owned by a user."""
    return (
        db.session.query(MedicationSchedule, Medication)
        #edit to chek logic
        .join(Medication, MedicationSchedule.medication_id == Medication.id)
        .filter(
            Medication.user_id == user_id,
            MedicationSchedule.is_active.is_(True),
        )
        .all()
    )


def find_dose(schedule_id, scheduled_time):
    """The Dose row for one occurrence, or None if it was never created."""
    return Dose.query.filter_by(
        #resolved logc err from scheduled_time = scheduled_time to:
        schedule_id=schedule_id, scheduled_for=scheduled_time
    ).first()


def _reminder_dict(schedule, medication, when, dose, now):
    minutes_until = int((when - now).total_seconds() // 60)
    return {
        "schedule_id": schedule.id,
        "dose_id": dose.id if dose else None,
        "medication_id": medication.id,
        "medication_name": medication.name,
        "dosage": medication.dosage,
        "scheduled_time": when.isoformat(),
        "minutes_until": minutes_until,
        "status": "overdue" if minutes_until < 0 else "upcoming",
    }


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def get_reminders(user_id, window_minutes=60, overdue_minutes=60, now=None):
    """Reminders from `overdue_minutes` ago up to `window_minutes` ahead.

    Doses already taken (or already missed) are left out. The window may
    cross midnight, so today and tomorrow are both checked.
    """
    now = now or datetime.now()
    start = now - timedelta(minutes=overdue_minutes)
    end = now + timedelta(minutes=window_minutes)

    reminders = []
    for schedule, medication in user_schedules(user_id):
        for day in {start.date(), now.date(), end.date()}:
            if not occurs_on(schedule, day):
                continue
            when = occurrence_datetime(schedule, day)
            if not (start <= when <= end):
                continue

            dose = find_dose(schedule.id, when)
            if dose and (dose.status or "pending").lower() != "pending":
                continue  # already taken or already marked missed
            reminders.append(_reminder_dict(schedule, medication, when, dose, now))

    reminders.sort(key=lambda r: r["scheduled_time"])
    return reminders


def get_upcoming_reminders(user_id, window_minutes=60, now=None):
    """Only doses that have not happened yet (next `window_minutes`)."""
    return [
        r for r in get_reminders(user_id, window_minutes, 0, now)
        if r["minutes_until"] >= 0
    ]


def get_due_reminders(user_id, overdue_minutes=60, now=None):
    """Doses due right now: from `overdue_minutes` ago until this moment."""
    return [
        r for r in get_reminders(user_id, 0, overdue_minutes, now)
        if r["minutes_until"] <= 0
    ]


def generate_doses_for_date(user_id, day=None, commit=True):
    """Create 'pending' Dose rows for every schedule that runs on `day`.

    Reports and adherence need Dose rows to exist. Call this when a user opens
    the app or from a daily job. It is safe to run twice: existing rows are
    skipped. Returns the number of rows created.

    NOTE: the Dose model belongs to the Dose Tracking teammate. Confirm with
    them whether doses are pre-created (this function) or created on demand.
    """
    day = day or date.today()
    created = 0
    for schedule, _medication in user_schedules(user_id):
        if not occurs_on(schedule, day):
            continue
        when = occurrence_datetime(schedule, day)
        if find_dose(schedule.id, when):
            continue
        db.session.add(
            #resolved logc err fromm scheduled_time to scheduled_for
            Dose(schedule_id=schedule.id, scheduled_for=when, status="pending")
        )
        created += 1

    if commit and created:
        db.session.commit()
    return created