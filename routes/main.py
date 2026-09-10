from flask import Blueprint, render_template
from models.bed import Bed


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    vacant_beds = (
        Bed.query
        .filter_by(is_occupied=False)
        .all()
    )

    vacant_beds.sort(
        key=lambda bed: (
            bed.room.sharing_type,
            bed.room.building.name,
            bed.room.room_number,
            bed.bed_number
        )
    )

    return render_template(
        "home.html",
        vacant_beds=vacant_beds
    )