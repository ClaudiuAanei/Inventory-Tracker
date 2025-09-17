from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from ..models import Stock, Product
from ..utils.roles import require_role
from flask_jwt_extended import jwt_required
from .. import db

bp = Blueprint("products", __name__)

categories = {"no category", "category1", "category2", "category3"}

@bp.post('/products')
@jwt_required()
@require_role('manager', 'admin')
def create_product():
    data = request.get_json() or {}

    # Create SKU code
    lastid = Product.query.order_by(Product.id.desc()).first()
    next_id = lastid.id + 1 if lastid else 1
    sku = f"P-{next_id:04d}"

    name = data.get('name') or ""
    price = data.get('price') or ""
    category = data.get('category') or "no category"

    if not name or not price or category not in categories:
        return jsonify({
            "status": False,
            "msg": "You must fill the name and price and category must be one from options."
        }), 401

    if not isinstance(price, float) or price < 0:
        return jsonify({
            "status": False,
            "msg": "The price must be a number and/or higher than 0"
        }), 401

    # Create product and add to database
    new_product = Product(name= name,
                          sku= sku,
                          price= price,
                          category= category if category in categories else "No Category")

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "status": True,
        "msg": "New product was successfuly created.",
        "data": {"id": new_product.id,
                 "name": new_product.name,
                 "sku": new_product.sku,
                 "price": new_product.price,
                 "category": new_product.category
                 },
    }), 201

@bp.get("/products")
@jwt_required()
@require_role('manager', 'admin', 'staff')
def list_products():
    prod = request.args.get("prod")
    category = request.args.get("category")
    page = max(1, request.args.get("page", default= 1, type= int))
    page_size = min(100, request.args.get("page_size", default=20, type= int))

    query = Product.query

    if prod:
        query = query.filter(Product.name.ilike(f"%{prod}%"))
    if category:
        query = query.filter(Product.category == category)

    items = query.paginate(page= page, per_page= page_size, error_out=False)

    return jsonify({
        "page": items.page,
        "page_size": items.per_page,
        "total": items.total,
        "total_pages": items.pages,
        "has_next": items.has_next,
        "has_prev": items.has_prev,
        "products": [
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "price": float(p.price),
                "category": p.category,
            }
            for p in items.items
        ]
    }), 200

@bp.get("/products/<int:pid>")
@jwt_required()
def details_product(pid):
    prod = Product.query.get(pid)
    warehouse_id = request.args.get("warehouse_id", type= int, default= 1)
    if not prod:
        return jsonify({"msg": "No product with that id"}), 404

    total_qty = (
        db.session.query(func.coalesce(func.sum(Stock.quantity), 0))
        .filter(Stock.product_id == pid)
        .scalar()
    )

    qty_in_wh = (
        db.session.query(func.coalesce(func.sum(Stock.quantity), 0))
        .filter(Stock.product_id == pid, Stock.warehouse_id == warehouse_id)
        .scalar()
    )

    return jsonify({
        "id": prod.id,
        "sku": prod.sku,
        "name": prod.name,
        "price": float(prod.price),
        "category": prod.category,
        "total_qty": total_qty,
        "qty_in_wh": qty_in_wh,
        "warehouse_id": warehouse_id
    }), 200

@bp.patch("/products/<int:pid>")
@jwt_required()
@require_role('manager', 'admin')
def update_product(pid):
    product = Product.query.get_or_404(pid)
    data = request.get_json()

    if "name" in data:
        product.name = data["name"] or ""
        if not product.name:
            return jsonify({"status": False, "msg": "Name required"})
    if "price" in data:
        product.price = data["price"] or ""
        if not product.price:
            return jsonify({"status": False, "msg": "Price is required"})
    if "category" in data:
        product.category = data["category"] or "no category"

    db.session.commit()
    return jsonify({
        "status": True,
        "msg": "Product updated",
        "data" :
            {"name": product.name,
            "sku": product.sku,
            "price": float(product.price),
            }
        }), 200

@bp.delete("/products/<int:pid>")
@jwt_required()
@require_role('manager', 'admin')
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status":False, "msg":"Product have stocks in one ore more Warehouses"}), 409

    return jsonify({"status":True, "msg":"Product was succesfully deleted."}), 200