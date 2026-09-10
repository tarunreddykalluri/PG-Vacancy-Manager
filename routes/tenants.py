from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import or_
from datetime import date

from extensions import db
from models.bed import Bed
from models.tenant import Tenant
from models.room import Room


tenants_bp = Blueprint(
    "tenants",
    __name__,
    url_prefix="/tenants"
)


@tenants_bp.route("/")
def tenants():
    search = request.args.get("search", "").strip()

    query = (
        Tenant.query
        .join(Bed)
        .join(Room)
        .filter(Tenant.is_active == True)
    )

    if search:
        query = query.filter(
            or_(
                Tenant.name.ilike(f"%{search}%"),
                Tenant.phone.ilike(f"%{search}%"),
                Room.room_number.ilike(f"%{search}%"),
                Tenant.pg_name.ilike(f"%{search}%")
            )
        )

    tenants = query.order_by(Tenant.name).all()

    return render_template(
        "tenants.html",
        tenants=tenants,
        search=search
    )


@tenants_bp.route("/history")
def tenant_history():
    search = request.args.get("search", "").strip()

    query = (
        Tenant.query
        .outerjoin(Bed)
        .outerjoin(Room)
        .filter(Tenant.is_active == False)
    )

    if search:
        query = query.filter(
            or_(
                Tenant.name.ilike(f"%{search}%"),
                Tenant.phone.ilike(f"%{search}%"),
                Room.room_number.ilike(f"%{search}%"),
                Tenant.pg_name.ilike(f"%{search}%")
            )
        )

    tenants = query.order_by(Tenant.name).all()

    return render_template(
        "tenant_history.html",
        tenants=tenants,
        search=search
    )


@tenants_bp.route("/add/<int:bed_id>", methods=["GET", "POST"])
def add_tenant(bed_id):
    bed = Bed.query.get_or_404(bed_id)

    if bed.is_occupied:
        return redirect(url_for("vacancies.vacancies"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name or not phone:
            return render_template(
                "tenant_form.html",
                bed=bed,
                error="Name and phone are required."
            )

        tenant = Tenant(
            name=name,
            phone=phone,
            pg_name=bed.room.building.name,
            bed_id=bed.id,
            joining_date=date.today(),
            is_active=True
        )

        bed.is_occupied = True

        db.session.add(tenant)
        db.session.commit()

        return redirect(url_for("vacancies.vacancies"))

    return render_template(
        "tenant_form.html",
        bed=bed
    )


@tenants_bp.route("/vacate/<int:tenant_id>", methods=["POST"])
def vacate_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)

    if not tenant.is_active:
        return redirect(url_for("tenants.tenants"))

    bed = tenant.bed

    if bed:
        bed.is_occupied = False

    tenant.vacating_date = date.today()
    tenant.is_active = False

    db.session.commit()

    return redirect(url_for("tenants.tenants"))