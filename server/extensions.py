from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
api = Api()
