from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, UniqueConstraint  # type: ignore[reportMissingImports]

from extensions import db

PENDING = "pending"
TAKEN = "taken"
MISSED = "missed"
DOSE_STATUSES = (PENDING, TAKEN, MISSED)


def _utcnow():
    # Stored as naive UTC. Frontend converts to local time (Nairobi is UTC+3).
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Dose(db.Model):
    __tablename__ = "doses"
    __table_args__ = (
        UniqueConstraint("schedule_id", "scheduled_for", name="uq_dose_schedule_time"),
        CheckConstraint("status IN ('pending','taken','missed')", name="ck_dose_status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(
        db.Integer, db.ForeignKey("medication_schedules.id"), nullable=False, index=True
    )
    scheduled_for = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False, default=PENDING)
    taken_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_utcnow)

    schedule = db.relationship(
        "MedicationSchedule",
        backref=db.backref("doses", cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<Dose {self.id} {self.status} {self.scheduled_for}>"