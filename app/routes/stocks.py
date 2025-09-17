from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from .. import db
from ..models import WareHouse
from ..models import Product
from ..models import Stock

bp = Blueprint('stocks', __name__)

@bp.post('/stocks')
@jwt_required()
def add_stock():
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    warehouse_id = data.get("warehouse_id")
    quantity = data.get("quantity")

    if not product_id or not warehouse_id or not isinstance(quantity, int):
        return jsonify({"status": False, "msg": "product, warehouse or quntity is missing."})

    if not Product.query.filter_by(id=product_id).first():
        return jsonify({"status": False, "msg": "Product doesn't exists"}), 409
    if not WareHouse.query.filter_by(id=warehouse_id).first():
        return jsonify({"status": False, "msg": "The WareHouse doesn't exists"}), 409

    if quantity < 0:
        return jsonify({"status": False, "msg": "The quantity must be a number and/or higher than 0"})

    exists = Stock.query.filter_by(
        product_id=data["product_id"], warehouse_id=data["warehouse_id"]
    ).first()

    if exists:
        return jsonify({"status": False, "msg": "This product already have stock in this warehouse."})

    stk = Stock(
        product_id=data["product_id"],
        warehouse_id=data["warehouse_id"],
        quantity=data["quantity"],
    )
    db.session.add(stk)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": False, "msg": "Product already in stocks or something went wrong"})

    return jsonify({"status": True, "msg": "New stock successfuly added"})

@bp.get('/stocks')
@jwt_required()
def show_stocks():
    product_id = request.args.get("product_id", type= int)
    warehouse_id = request.args.get("warehouse_id", type= int)
    page = request.args.get("page", default= 1, type=int)
    per_page = request.args.get("per_page", default= 20, type=int)

    query = Stock.query
    if product_id is not None:
        query = query.filter(Stock.product_id == product_id)
    if warehouse_id is not None:
        query = query.filter(Stock.warehouse_id == warehouse_id)

    items = query.order_by(Stock.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [serialize_stock(s) for s in items.items],
        "page": items.page,
        "pages": items.pages,
        "total": items.total
    })

@bp.get('/stocks/<int:stock_id>')
@jwt_required()
def stocks_details(stock_id):
    s = Stock.query.get_or_404(stock_id)
    return jsonify(serialize_stock(s))

@bp.patch('/stocks/<int:stock_id>')
@jwt_required()
def update_stock(stock_id):
    s = Stock.query.get_or_404(stock_id)
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"status": True, "msg": "Nothing was changed"})

    new_product_id = data.get("product_id", s.product_id)
    new_warehouse_id = data.get("warehouse_id", s.warehouse_id)

    if (new_product_id, new_warehouse_id) != (s.product_id, s.warehouse_id):
        if not Product.query.get(new_product_id):
            return jsonify({"status": False, "msg": "Product doesn't exists."})
        if not Product.query.get(new_warehouse_id):
            return jsonify({"status": False, "msg": "Warehouse doesn't exists."})

        duplicate = Stock.query.filter_by(
            product_id=new_product_id, warehouse_id=new_warehouse_id
        ).first()

        if duplicate and duplicate.id != s.id:
            return jsonify({"status": False, "msg": "Already exists a stock with this product_id and warehouse_id"})


    if "quantity" in data:
        if s.quantity + data["quantity"] < 0:
            return jsonify({"status": False, "msg": "Quantity can't be a negative number"})
        s.quantity += data["quantity"]


    s.product_id = new_product_id
    s.warehouse_id = new_warehouse_id

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": False, "msg": ""}), 409
    return jsonify({"status": True,
                    "update": serialize_stock(s),
                    "msg": "Stock Successfuly updated"})

@bp.delete('/stocks/<int:stock_id>')
@jwt_required()
def delete_stock(stock_id):
    s = Stock.query.get_or_404(stock_id)
    db.session.delete(s)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify("You can't delete this stock because of conections.")

    return jsonify({"status": True ,"msg":"Stock deleted successfuly"}), 200

def serialize_stock(s: Stock) -> dict:
    return{
        "id": s.id,
        "product_name": getattr(s.product, "name", None),
        "product_id": s.product_id,
        "warehouse_id": s.warehouse_id,
        "warehouse_name": getattr(s.warehouse, "name", None),
        "quantity": s.quantity,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }