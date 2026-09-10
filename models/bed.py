from extensions import db


class Bed(db.Model):
    __tablename__ = "beds"

    id = db.Column(db.Integer, primary_key=True)
    bed_number = db.Column(db.Integer, nullable=False)

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id"),
        nullable=False
    )

    is_occupied = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    tenants = db.relationship(
        "Tenant",
        backref="bed",
        lazy=True
    )

    def __repr__(self):
        return f"<Bed {self.bed_number}>"