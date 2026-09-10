from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models.room import Room
from models.bed import Bed
from models.building import Building


rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")


@rooms_bp.route("/add/<int:building_id>", methods=["GET", "POST"])
def add_room(building_id):
    building = Building.query.get_or_404(building_id)

    if request.method == "POST":
        room_number = request.form.get("room_number", "").strip()
        sharing_type = request.form.get("sharing_type", "").strip()

        if not room_number:
            return render_template(
                "add_room.html",
                building=building,
                error="Room number is required."
            )

        if not sharing_type or not sharing_type.isdigit():
            return render_template(
                "add_room.html",
                building=building,
                error="Please select a sharing type."
            )

        sharing_type = int(sharing_type)

        if sharing_type < 1:
            return render_template(
                "add_room.html",
                building=building,
                error="Invalid sharing type."
            )

        room = Room(
            room_number=room_number,
            sharing_type=sharing_type,
            building_id=building.id
        )

        db.session.add(room)
        db.session.flush()

        # Automatically create beds according to sharing type
        for bed_number in range(1, sharing_type + 1):
            bed = Bed(
                bed_number=bed_number,
                room_id=room.id,
                is_occupied=False
            )

            db.session.add(bed)

        db.session.commit()

        return redirect(
            url_for(
                "buildings.building_detail",
                building_id=building.id
            )
        )

    return render_template(
        "add_room.html",
        building=building
    )