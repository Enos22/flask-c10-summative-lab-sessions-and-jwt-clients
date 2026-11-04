# Configuration values are loaded by create_app() in app/__init__.py.
# Keep this module for any existing imports that expect app.config.
import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-development-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
