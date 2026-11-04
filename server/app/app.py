# Backwards-compatible entry point for scripts that previously imported
# `app` from app.app. The canonical factory lives in app/__init__.py.
from app import create_app
from extensions import db

app = create_app()
