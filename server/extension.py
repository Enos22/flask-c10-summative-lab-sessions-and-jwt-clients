# Backwards-compatible imports. Use extensions.py as the single source
# of SQLAlchemy, Bcrypt, Migrate and Flask-RESTful instances.
from extensions import api, bcrypt, db, migrate

__all__ = ["api", "bcrypt", "db", "migrate"]
