"""Session-protected adherence, history and reminder reports."""
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Blueprint, jsonify, request, session

from services import adherence_service, reminder_service

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            return jsonify(error="Authentication required."), 401
        return view(*args, **kwargs)
    return wrapped


def parse_date(value, default):
    if not value:
        return default, None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except ValueError:
        return None, f"Invalid date '{value}'. Use YYYY-MM-DD."


def parse_int(name, default, minimum=0, maximum=10000):
    raw = request.args.get(name)
    if raw is None:
        return default, None
    try:
        number = int(raw)
    except ValueError:
        return None, f"'{name}' must be a whole number."
    if not minimum <= number <= maximum:
        return None, f"'{name}' must be between {minimum} and {maximum}."
    return number, None


def date_range(default_days=7):
    today = date.today()
    end, err = parse_date(request.args.get("end"), today)
    if err:
        return None, None, err
    start, err = parse_date(
        request.args.get("start"), end - timedelta(days=default_days - 1)
    )
    if err:
        return None, None, err
    if start > end:
        return None, None, "'start' must not be after 'end'."
    if (end - start).days > 366:
        return None, None, "Date range cannot exceed one year."
    return start, end, None


def error(message, status=400):
    return jsonify(error=message), status


@reports_bp.get("/daily")
@login_required
def daily_report():
    day, err = parse_date(request.args.get("date"), date.today())
    if err:
        return error(err)
    user_id = session["user_id"]
    if day == date.today():
        reminder_service.generate_doses_for_date(user_id, day)
    doses = adherence_service.fetch_dose_dicts(user_id, day, day)
    return jsonify(
        date=day.isoformat(),
        summary=adherence_service.summarize(d["status"] for d in doses),
        taken=[d for d in doses if d["status"] == "taken"],
        missed=[d for d in doses if d["status"] == "missed"],
        pending=[d for d in doses if d["status"] == "pending"],
    )


@reports_bp.get("/history")
@login_required
def history_report():
    start, end, err = date_range()
    if err:
        return error(err)
    return jsonify(
        start=start.isoformat(),
        end=end.isoformat(),
        days=adherence_service.daily_history(session["user_id"], start, end),
    )


@reports_bp.get("/adherence")
@login_required
def adherence_report():
    days, err = parse_int("days", 30, minimum=1, maximum=366)
    if err:
        return error(err)
    end = date.today()
    start = end - timedelta(days=days - 1)
    return jsonify(
        adherence_service.calculate_adherence(session["user_id"], start, end)
    )


@reports_bp.get("/missed")
@login_required
def missed_doses():
    start, end, err = date_range()
    if err:
        return error(err)
    doses = adherence_service.fetch_dose_dicts(session["user_id"], start, end)
    missed = [d for d in doses if d["status"] == "missed"]
    missed.sort(key=lambda d: d["scheduled_time"], reverse=True)
    return jsonify(start=start.isoformat(), end=end.isoformat(),
                   count=len(missed), doses=missed)


@reports_bp.get("/completed")
@login_required
def completed_doses():
    start, end, err = date_range()
    if err:
        return error(err)
    doses = adherence_service.fetch_dose_dicts(session["user_id"], start, end)
    taken = [d for d in doses if d["status"] == "taken"]
    taken.sort(key=lambda d: d["scheduled_time"], reverse=True)
    return jsonify(start=start.isoformat(), end=end.isoformat(),
                   count=len(taken), doses=taken)


@reports_bp.get("/reminders/upcoming")
@login_required
def upcoming_reminders():
    minutes, err = parse_int("minutes", 60, minimum=1, maximum=1440)
    if err:
        return error(err)
    reminders = reminder_service.get_upcoming_reminders(session["user_id"], minutes)
    return jsonify(window_minutes=minutes, count=len(reminders), reminders=reminders)


@reports_bp.get("/reminders/due")
@login_required
def due_reminders():
    overdue, err = parse_int("overdue", 60, minimum=1, maximum=1440)
    if err:
        return error(err)
    reminders = reminder_service.get_due_reminders(session["user_id"], overdue)
    return jsonify(overdue_minutes=overdue, count=len(reminders), reminders=reminders)
