from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models.building import Building
from models.bed import Bed
from models.tenant import Tenant


buildings_bp = Blueprint(
    "buildings",
    __name__,
    url_prefix="/buildings"
)


@buildings_bp.route("/")
def buildings():
    buildings = Building.query.order_by(Building.name).all()

    building_stats = []

    for building in buildings:
        total_rooms = len(building.rooms)

        total_beds = sum(
            len(room.beds)
            for room in building.rooms
        )

        occupied_beds = sum(
            1
            for room in building.rooms
            for bed in room.beds
            if bed.is_occupied
        )

        vacant_beds = total_beds - occupied_beds

        vacancy_percentage = (
            round((vacant_beds / total_beds) * 100)
            if total_beds > 0
            else 0
        )

        building_stats.append({
            "building": building,
            "total_rooms": total_rooms,
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "vacant_beds": vacant_beds,
            "vacancy_percentage": vacancy_percentage
        })

    return render_template(
        "buildings.html",
        building_stats=building_stats
    )


@buildings_bp.route("/add", methods=["GET", "POST"])
def add_building():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()

        if not name:
            return render_template(
                "add_building.html",
                error="Building name is required."
            )

        building = Building(
            name=name,
            address=address if address else None
        )

        db.session.add(building)
        db.session.commit()

        return redirect(url_for("buildings.buildings"))

    return render_template("add_building.html")


@buildings_bp.route("/<int:building_id>")
def building_detail(building_id):
    building = Building.query.get_or_404(building_id)

    total_rooms = len(building.rooms)

    total_beds = sum(
        len(room.beds)
        for room in building.rooms
    )

    occupied_beds = sum(
        1
        for room in building.rooms
        for bed in room.beds
        if bed.is_occupied
    )

    vacant_beds = total_beds - occupied_beds

    vacancy_percentage = (
        round((vacant_beds / total_beds) * 100)
        if total_beds > 0
        else 0
    )

    return render_template(
        "building_detail.html",
        building=building,
        total_rooms=total_rooms,
        total_beds=total_beds,
        occupied_beds=occupied_beds,
        vacant_beds=vacant_beds,
        vacancy_percentage=vacancy_percentage
    )


@buildings_bp.route("/delete/<int:building_id>", methods=["POST"])
def delete_building(building_id):
    building = Building.query.get_or_404(building_id)

    # Collect all beds belonging to this building
    building_beds = [
        bed
        for room in building.rooms
        for bed in room.beds
    ]

    # Do not allow deletion if this building has tenant history.
    # This protects tenant records from losing their room/bed information.
    tenant_count = Tenant.query.filter(
        Tenant.bed_id.in_([bed.id for bed in building_beds])
    ).count() if building_beds else 0

    if tenant_count > 0:
        return redirect(
            url_for(
                "buildings.building_detail",
                building_id=building.id,
                error="This building cannot be removed because it has tenant history."
            )
        )

    db.session.delete(building)
    db.session.commit()

    return redirect(url_for("buildings.buildings"))