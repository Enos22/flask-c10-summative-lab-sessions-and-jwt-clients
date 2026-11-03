from datetime import date, datetime, timedelta
import unittest
from uuid import uuid4

from app.app import app, db


class BackendApiTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite://")
        self.app_context = app.app_context()
        self.app_context.push()
        db.session.remove()
        db.drop_all()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_user(self, client):
        username = f"user_{uuid4().hex[:12]}"
        response = client.post(
            "/signup",
            json={
                "username": username,
                "password": "SecurePass1",
                "password_confirmation": "SecurePass1",
            },
        )
        self.assertEqual(response.status_code, 201)
        return username

    def create_medication(self, name="Test medication"):
        response = self.client.post(
            "/api/medications/addmedication",
            json={
                "name": name,
                "dosage": "1 tablet",
                "start_date": date.today().isoformat(),
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.json["medication"]

    def test_authentication_session_lifecycle(self):
        self.assertEqual(self.client.get("/check_session").status_code, 401)

        username = self.create_user(self.client)
        self.assertEqual(self.client.get("/check_session").status_code, 200)
        self.assertEqual(self.client.delete("/logout").status_code, 204)
        self.assertEqual(self.client.get("/check_session").status_code, 401)

        response = self.client.post(
            "/login",
            json={"username": username, "password": "SecurePass1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], username)

    def test_medications_are_scoped_to_the_logged_in_user(self):
        self.create_user(self.client)
        medication = self.create_medication()
        owner_medications = self.client.get("/api/medications/getmedications")
        self.assertEqual(owner_medications.status_code, 200)
        self.assertEqual(
            [item["id"] for item in owner_medications.json["medications"]],
            [medication["id"]],
        )

        other_user = app.test_client()
        self.create_user(other_user)
        other_medications = other_user.get("/api/medications/getmedications")
        self.assertEqual(other_medications.status_code, 200)
        self.assertEqual(other_medications.json["medications"], [])
        self.assertEqual(
            other_user.get(
                f"/api/medications/getmedication/{medication['id']}"
            ).status_code,
            404,
        )

    def test_schedule_generates_dose_and_updates_reports(self):
        self.create_user(self.client)
        medication = self.create_medication()
        now = datetime.now()
        today = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][now.weekday()]
        scheduled_time = (now - timedelta(minutes=5)).strftime("%H:%M")

        schedule_response = self.client.post(
            "/api/schedules",
            json={
                "medication_id": medication["id"],
                "reminder_time": scheduled_time,
                "days_of_week": [today],
            },
        )
        self.assertEqual(schedule_response.status_code, 201)

        report_response = self.client.get("/api/reports/daily")
        self.assertEqual(report_response.status_code, 200)
        report = report_response.json
        self.assertEqual(report["summary"]["total"], 1)
        dose = report["pending"][0]

        response = self.client.patch(
            f"/api/doses/{dose['dose_id']}/taken", json={}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "taken")

        completed = self.client.get("/api/reports/completed")
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.json["count"], 1)
        self.assertEqual(completed.json["doses"][0]["dose_id"], dose["dose_id"])
