from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models.room import Room
from models.bed import Bed
from models.building import Building
from models.tenant import Tenant


rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")


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

    room_number = str(room.room_number).strip()

    if room_number.isdigit():
        return (0, int(room_number))

    return (1, room_number.lower())


def sort_beds(beds):
    """
    Sort beds by bed number.
    """
    return sorted(
        beds,
        key=lambda bed: bed.bed_number
    )


@rooms_bp.route("/add/<int:building_id>", methods=["GET", "POST"])
def add_room(building_id):

    building = Building.query.get_or_404(building_id)

    if request.method == "POST":

        room_number = request.form.get(
            "room_number",
            ""
        ).strip()

        sharing_type = request.form.get(
            "sharing_type",
            ""
        ).strip()

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

        # Prevent duplicate room numbers inside the same building
        existing_room = Room.query.filter_by(
            building_id=building.id,
            room_number=room_number
        ).first()

        if existing_room:

            return render_template(
                "add_room.html",
                building=building,
                error="This room number already exists in this building."
            )

        room = Room(
            room_number=room_number,
            sharing_type=sharing_type,
            building_id=building.id
        )

        db.session.add(room)
        db.session.flush()

        # Automatically create beds
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


@rooms_bp.route("/edit/<int:room_id>", methods=["GET", "POST"])
def edit_room(room_id):

    room = Room.query.get_or_404(room_id)

    building = room.building

    if request.method == "POST":

        room_number = request.form.get(
            "room_number",
            ""
        ).strip()

        sharing_type = request.form.get(
            "sharing_type",
            ""
        ).strip()

        if not room_number:

            return render_template(
                "edit_room.html",
                room=room,
                building=building,
                error="Room number is required."
            )

        if not sharing_type or not sharing_type.isdigit():

            return render_template(
                "edit_room.html",
                room=room,
                building=building,
                error="Please select a sharing type."
            )

        new_sharing_type = int(sharing_type)

        if new_sharing_type < 1:

            return render_template(
                "edit_room.html",
                room=room,
                building=building,
                error="Invalid sharing type."
            )

        # Check duplicate room number
        existing_room = Room.query.filter(
            Room.building_id == building.id,
            Room.room_number == room_number,
            Room.id != room.id
        ).first()

        if existing_room:

            return render_template(
                "edit_room.html",
                room=room,
                building=building,
                error="This room number already exists in this building."
            )

        current_sharing_type = room.sharing_type

        # -------------------------------------------------
        # If sharing is increased
        # -------------------------------------------------

        if new_sharing_type > current_sharing_type:

            for bed_number in range(
                current_sharing_type + 1,
                new_sharing_type + 1
            ):

                bed = Bed(
                    bed_number=bed_number,
                    room_id=room.id,
                    is_occupied=False
                )

                db.session.add(bed)

        # -------------------------------------------------
        # If sharing is decreased
        # -------------------------------------------------

        elif new_sharing_type < current_sharing_type:

            beds_to_remove = Bed.query.filter(
                Bed.room_id == room.id,
                Bed.bed_number > new_sharing_type
            ).order_by(
                Bed.bed_number.desc()
            ).all()

            for bed in beds_to_remove:

                # Never remove an occupied bed
                if bed.is_occupied:

                    return render_template(
                        "edit_room.html",
                        room=room,
                        building=building,
                        error=(
                            f"Cannot reduce this room to "
                            f"{new_sharing_type} sharing because "
                            f"Bed {bed.bed_number} is currently occupied."
                        )
                    )

                # Never remove a bed that has tenant history
                tenant_history_exists = Tenant.query.filter_by(
                    bed_id=bed.id
                ).first()

                if tenant_history_exists:

                    return render_template(
                        "edit_room.html",
                        room=room,
                        building=building,
                        error=(
                            f"Cannot remove Bed {bed.bed_number} "
                            f"because it has tenant history."
                        )
                    )

                db.session.delete(bed)

        # Update room information
        room.room_number = room_number
        room.sharing_type = new_sharing_type

        db.session.commit()

        return redirect(
            url_for(
                "buildings.building_detail",
                building_id=building.id
            )
        )

    return render_template(
        "edit_room.html",
        room=room,
        building=building
    )