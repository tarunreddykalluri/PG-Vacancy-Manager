from extensions import db

class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False)

    sharing_type = db.Column(db.Integer, nullable=False)

    building_id = db.Column(
        db.Integer,
        db.ForeignKey("buildings.id"),
        nullable=False
    )

    beds = db.relationship(
        "Bed",
        backref="room",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Room {self.room_number}>"