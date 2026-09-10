from extensions import db

class Building(db.Model):
    __tablename__ = "buildings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)

    rooms = db.relationship(
        "Room",
        backref="building",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Building {self.name}>"