from extensions import db

DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


class MedicationSchedule(db.Model):
    __tablename__ = "medication_schedules"

    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(
        db.Integer, db.ForeignKey("medications.id"), nullable=False
    )
    reminder_time = db.Column(db.Time, nullable=False)

    days = db.Column(db.String(27), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


    medication = db.relationship(
        "Medication",
        backref=db.backref("schedules", cascade="all, delete-orphan"),
    )

    @property
    def days_list(self):
        return self.days.split(",") if self.days else []

    @days_list.setter
    def days_list(self, value):
        chosen = set(value)
        self.days = ",".join(d for d in DAY_ORDER if d in chosen)

    def __repr__(self):
        return f"<MedicationSchedule {self.id} med={self.medication_id} {self.reminder_time} {self.days}>"
    