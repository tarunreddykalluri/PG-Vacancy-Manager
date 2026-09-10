from extensions import db
from datetime import date


class Tenant(db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    pg_name = db.Column(
        db.String(100),
        nullable=True
    )

    bed_id = db.Column(
        db.Integer,
        db.ForeignKey("beds.id"),
        nullable=True
    )

    joining_date = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

    vacating_date = db.Column(
        db.Date,
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    def __repr__(self):
        return f"<Tenant {self.name}>"