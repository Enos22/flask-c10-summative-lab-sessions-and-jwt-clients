from datetime import date, time

from app.app import app, db
from models.medication import Medication
from models.medication_schedule import DAY_ORDER, MedicationSchedule
from models.user import User
from services.reminder_service import generate_doses_for_date

SEED_USERNAME = "Group_5"
SEED_PASSWORD = "Group_5@2026"


def seed_database():
    with app.app_context():
        db.create_all()

        user = User.query.filter_by(username=SEED_USERNAME).first()
        created_user = user is None
        if created_user:
            user = User(username=SEED_USERNAME)
            user.password_hash = SEED_PASSWORD
            db.session.add(user)
            db.session.flush()

        medications = (
            {
                "name": "Daily Vitamin",
                "dosage": "1 tablet",
                "instructions": "Take with food",
                "start_date": date.today(),
            },
            {
                "name": "Evening Medication",
                "dosage": "1 capsule",
                "instructions": "Take in the evening",
                "start_date": date.today(),
            },
        )

        for medication_data in medications:
            medication = Medication.query.filter_by(
                user_id=user.id, name=medication_data["name"]
            ).first()
            if medication is None:
                medication = Medication(user_id=user.id, **medication_data)
                db.session.add(medication)
                db.session.flush()

            for reminder_time in (time(8, 0), time(20, 0)):
                schedule = MedicationSchedule.query.filter_by(
                    medication_id=medication.id,
                    reminder_time=reminder_time,
                    days=",".join(DAY_ORDER),
                ).first()
                if schedule is None:
                    db.session.add(
                        MedicationSchedule(
                            medication_id=medication.id,
                            reminder_time=reminder_time,
                            days=",".join(DAY_ORDER),
                            is_active=True,
                        )
                    )

        db.session.commit()
        generate_doses_for_date(user.id)

        print(f"Seed data ready for user '{SEED_USERNAME}'.")
        if created_user:
            print(f"Demo password: {SEED_PASSWORD}")
        else:
            print("Existing demo user reused; password was not changed.")


if __name__ == "__main__":
    seed_database()