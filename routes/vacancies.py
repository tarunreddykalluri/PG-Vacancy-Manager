from flask import Blueprint, render_template, request
from models.bed import Bed
from models.building import Building


vacancies_bp = Blueprint(
    "vacancies",
    __name__,
    url_prefix="/vacancies"
)


def room_sort_key(room):
    """
    Sort room numbers naturally.

    Example:
    2
    3
    11
    20
    101
    """

    room_number = str(
        room.room_number
    ).strip()

    if room_number.isdigit():
        return (0, int(room_number))

    return (1, room_number.lower())


@vacancies_bp.route("/")
def vacancies():

    selected_building_id = request.args.get(
        "building_id",
        type=int
    )


    # Get buildings for the filter dropdown
    buildings = Building.query.order_by(
        Building.name
    ).all()


    # Get vacant beds
    vacant_beds = (
        Bed.query
        .filter_by(is_occupied=False)
        .all()
    )


    # Filter by selected building
    if selected_building_id:

        vacant_beds = [
            bed
            for bed in vacant_beds
            if bed.room.building_id ==
            selected_building_id
        ]


    # Sort vacancies properly
    vacant_beds.sort(
        key=lambda bed: (
            bed.room.sharing_type,
            bed.room.building.name.lower(),
            room_sort_key(bed.room),
            bed.bed_number
        )
    )


    return render_template(
        "vacancies.html",
        vacant_beds=vacant_beds,
        buildings=buildings,
        selected_building_id=selected_building_id
    )