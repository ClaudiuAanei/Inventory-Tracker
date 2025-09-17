from flask import Blueprint, request, jsonify
from ..models import StockMovement, Stock
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..utils.roles import require_role
from .. import db

bp = Blueprint("stock-movement", __name__)

@bp.post("/stock-movements")
@jwt_required()
@require_role("admin","manager")
def create_stock_movements():
    data = request.get_json(silent=True) or {}

    product_id = data.get("product_id")
    warehouse_id = data.get("warehouse_id") or ""
    move_type = data.get("move_type") or ""
    quantity = data.get("quantity") or 0
    reason = data.get("reason") or ""


    identity = get_jwt_identity()

    if not product_id or not warehouse_id:
        return jsonify({"status": False, "msg": "warehouse_id and product_id are mandatory."})

    if not quantity:
        return jsonify({"status": False, "msg": "You need to add quantity"})

    stock = Stock.query.filter_by(product_id=product_id, warehouse_id=warehouse_id).first()

    if not stock:
        return jsonify({"status": False, "msg": "No stock with this id. You must create product or a stock for."})

    if move_type == 'IN' and quantity > 0:
        stock.quantity += quantity

    elif move_type == "ADJUST_ABS" and quantity > 0:
        stock.quantity = quantity

    elif move_type == "OUT" and quantity > 0:
        if stock.quantity > quantity:
            stock.quantity -= quantity

    elif move_type == "ADJUST_REL":
        if stock.quantity + quantity > 0:
            stock.quantity += quantity
    else:
        return jsonify(
            {"status": False,
             "msg": "Movements can be only: IN/OUT/ADJUST_ABS/ADJUST_REL and quantity must be higher than 0"})

    new_movement = StockMovement(type= move_type,
                                 quantity=quantity,
                                 reason=reason,
                                 product_id=product_id,
                                 warehouse_id=warehouse_id,
                                 actor_user_id= identity)

    db.session.add(new_movement)
    db.session.commit()

    return jsonify({"status": True, "msg": "Stock movement successfully created."})

@bp.get("/stock-movements")
@jwt_required()
def list_stock_movements():
    product_id = request.args.get("product_id")
    warehouse_id = request.args.get("warehouse_id")
    move_type = request.args.get("move_type")
    from_wh = request.args.get("from_wh")
    to_wh = request.args.get("to_wh")
    actor_user_id = request.args.get("user_id")

    page = max(1, request.args.get("page", default= 1, type= int))
    per_page = min(100, request.args.get("page_size", default=20, type= int))

    movements = filter_movements(product_id=product_id,
                                 warehouse_id=warehouse_id,
                                 move_type=move_type,
                                 from_wh=from_wh,
                                 to_wh=to_wh,
                                 actor_user_id=actor_user_id)

    items = movements.order_by(StockMovement.created_at.desc()).paginate(page=page, per_page=per_page)

    return jsonify({"status": True,
                    "movements": [serialize_movements(movement) for movement in items.items],
                    "page": items.page,
                    "pages": items.pages,
                    "total": items.total})

def filter_movements(**kwargs):
    movements = StockMovement.query

    if kwargs["product_id"]:
        movements.filter(StockMovement.product_id == kwargs["product_id"])
    if kwargs["warehouse_id"]:
        movements.filter(StockMovement.warehouse_id == kwargs["warehouse_id"])
    if kwargs["move_type"]:
        movements.filter(StockMovement.type == kwargs["move_type"])
    if kwargs["from_wh"]:
        movements.filter(StockMovement.related_transfer_id.source_warehouse_id == kwargs["from_wh"])
    if kwargs["to_wh"]:
        movements.filter(StockMovement.related_transfer_id.dest_warehouse_id == kwargs["to_wh"])
    if kwargs["actor_user_id"]:
        movements.filter(StockMovement.actor_user_id == kwargs["actor_user_id"])

    return movements

def serialize_movements(movements: StockMovement) -> dict:
    related_transfer = movements.transfer
    return{
        "type": movements.type,
        "transfer": None if related_transfer is None else{
            "id": related_transfer.id,
            "status": related_transfer.status,
            "source_warehouse_id": related_transfer.source_warehouse_id,
            "dest_warehouse_id": related_transfer.dest_warehouse_id
        },
        "warehouse_id": movements.warehouse_id,
        "product_id": movements.product_id,
        "actor_user_id": movements.actor_user_id,
        "reason": movements.reason,
        "created_at": movements.created_at
    }

