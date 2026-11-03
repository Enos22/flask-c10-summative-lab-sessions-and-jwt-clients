#Benson

from extensions import db


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    dosage = db.Column(db.String(100), nullable=False)

    instructions = db.Column(db.Text, nullable=True)

    start_date = db.Column(db.Date, nullable=False)

    end_date = db.Column(db.Date, nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    user = db.relationship(
        "User",
        backref=db.backref("medications", lazy=True)
    )

    def __repr__(self):
        return f"<Medication {self.name}>"