from sqlalchemy.ext.hybrid import hybrid_property
from app.config import db, bcrypt

class User(db.Model):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    _password_hash = db.Column(db.String)

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        if not password:
            raise ValueError("Password is Required")
        if len(password) < 8:
            raise ValueError("Password must be atleast 8 Characters")
        if len(password) > 32:
            raise ValueError("Password must be less than 32 characters")
        if password.strip() != password:
            raise ValueError("Password cannot start or End with spaces")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must have an uppercase letter!")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must have a Number")

        self._password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        ).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )


    def __repr__(self):
        return f'<User {self.username}>'
