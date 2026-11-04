import os

from flask import Flask
from flask_cors import CORS

from extensions import api, bcrypt, db, migrate


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-development-secret"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///app.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if test_config:
        app.config.update(test_config)

    # React runs on localhost:4000. Credentials are required for Flask sessions.
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:4000"]}},
        supports_credentials=True,
    )

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Import models before create_all / migrations discover the metadata.
    from models.user import User  # noqa: F401
    from models.medication import Medication  # noqa: F401
    from models.medication_schedule import MedicationSchedule  # noqa: F401
    from models.dose import Dose  # noqa: F401

    # Register each blueprint exactly once.
    from routes.medication_routes import medications_bp
    from routes.dose_routes import dose_bp
    from routes.schedules import schedules_bp
    from routes.reports_routes import reports_bp

    app.register_blueprint(medications_bp)
    app.register_blueprint(dose_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(reports_bp)

    # Flask-RESTful authentication resources.
    from routes.auth_routes import (
        Signup, Login, Logout, CheckSession, ClearSession
    )

    api.add_resource(Signup, "/signup", endpoint="signup")
    api.add_resource(Login, "/login", endpoint="login")
    api.add_resource(Logout, "/logout", endpoint="logout")
    api.add_resource(CheckSession, "/check_session", endpoint="check_session")
    api.add_resource(ClearSession, "/clear", endpoint="clear_session")
    api.init_app(app)

    with app.app_context():
        db.create_all()

    return app
