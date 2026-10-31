from app.extensions import db

 
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
