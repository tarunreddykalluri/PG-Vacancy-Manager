from flask import Blueprint, render_template
from models.bed import Bed


vacancies_bp = Blueprint(
    "vacancies",
    __name__,
    url_prefix="/vacancies"
)


@vacancies_bp.route("/")
def vacancies():
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
        "vacancies.html",
        vacant_beds=vacant_beds
    )