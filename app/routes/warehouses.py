from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from ..utils.roles import require_role
from flask_jwt_extended import jwt_required
from ..models.warehouses import WareHouse
from .. import db

bp = Blueprint("warehouse", __name__)

@bp.post("/warehouses")
@jwt_required()
@require_role("admin", "manager")
def create_warehouse():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    location = (data.get("location") or "").strip()

    errors = {}
    if not name or not isinstance(name, str) or len(name) > 30:
        errors["name"] = "Field name can not be empty or longer than 30 char"
    if not location or not isinstance(location, str) or len(location) > 200:
        errors["location"] = "Field location can not be empty or longer that 200 char"
    if errors:
        return jsonify(error="validation_error", fields=errors), 422

    wh = WareHouse(name=name, location=location)
    try:
        db.session.add(wh)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": False,
                        "msg": "WareHouse with this name is already exists in the company"}), 409
    except Exception:
        db.session.rollback()
        return jsonify(error="server_error"), 500

    response = jsonify({"status": True,
                    "msg": "WareHouse created.",
                    "data": {"id": wh.id, "name": wh.name, "location": wh.location},
                    })
    response.headers["Location"] = f"warehouses/{wh.id}"

    return response, 201

@bp.get("/warehouses")
@jwt_required()
@require_role("manager", "admin", "staff")
def list_warehouses():
    name = request.args.get("name")
    page = max(1, request.args.get("page", default= 1, type= int))
    page_size = min(100, request.args.get("page_size", default=20, type= int))

    query = WareHouse.query

    if name:
        query = query.filter(WareHouse.lower(name).ilike(f"%{name.strip()}%"))
    query = query.order_by(WareHouse.name.asc())

    warehouses = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        "page": warehouses.page,
        "page_size": warehouses.per_page,
        "total": warehouses.total,
        "total_pages": warehouses.pages,
        "has_next": warehouses.has_next,
        "has_prev": warehouses.has_prev,
        "warehouses": [
            {
                "id": wh.id,
                "name": wh.name,
                "location": wh.location
            }
            for wh in warehouses.items
        ]
    }), 200

@bp.get("/warehouses/<int:wh_id>")
@jwt_required()
def details_warehouse(wh_id):
    warehouse = WareHouse.query.filter_by(id=wh_id).first()

    if not warehouse:
        return jsonify({"status": False,"msg": "Warehouse not found."}), 404
    return jsonify({"id": warehouse.id,"name": warehouse.name,"location": warehouse.location}), 200

@bp.patch("/warehouses/<int:wh_id>")
@jwt_required()
@require_role("admin", "manager")
def update_warehouse(wh_id):
    wh = WareHouse.query.get_or_404(wh_id)
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    location = data.get("location")

    errors = {}
    if not name or len(name) > 30 or wh.name == name:
        errors["name"] = "Name field can't be empty, the same or larger than 30 characters"
    else:
        wh.name = name
    if location:
        wh.location = location
    if errors:
        return jsonify({"status": False, "msg": errors})

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": False, "msg":"This Warehouse is already exists."}), 409

    return jsonify(status=True, message="Warehouse updated.", data={
        "id": wh.id, "name": wh.name, "location": wh.location
    }), 200

@bp.delete("/warehouse/<int:wh_id>")
@jwt_required()
@require_role("manager")
def delete_warehouse(wh_id):
    ware_house = WareHouse.query.filter_by(id=wh_id).first()
    if not ware_house:
        return jsonify({"status": False,"error": "This WareHouse doesn't exists."}), 409
    try:
        db.session.delete(ware_house)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": False, "msg": "WareHouse still has products in."}), 409

    return jsonify({"status": True, "msg":"WareHouse was successfuly removed."}), 200