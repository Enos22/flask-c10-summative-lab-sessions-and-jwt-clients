import sys
from pathlib import Path

server_dir = Path(__file__).resolve().parents[1]
repository_dir = server_dir.parent
sys.path.insert(0, str(server_dir))
sys.path.insert(0, str(repository_dir))

from app.config import app, db

import extensions
extensions.db = db

import models
from models import dose, medication, medication_schedule, user

sys.modules["server.extensions"] = extensions
sys.modules["server.models"] = models
for model_module in (dose, medication, medication_schedule, user):
    sys.modules[f"server.models.{model_module.__name__.rsplit('.', 1)[-1]}"] = (
        model_module
    )

from routes import auth_routes
from routes.dose_routes import dose_bp
from routes.medication_routes import medications_bp
from routes.reports_routes import reports_bp
from routes.schedules import schedules_bp

app.register_blueprint(medications_bp)
app.register_blueprint(schedules_bp)
app.register_blueprint(dose_bp)
app.register_blueprint(reports_bp)