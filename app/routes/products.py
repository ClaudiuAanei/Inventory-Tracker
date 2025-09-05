from flask import Blueprint, jsonify, request

from ..models import WareHouse
from ..utils.roles import require_role
from flask_jwt_extended import jwt_required
from ..models.product import Product
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
    warehouse_id = data.get("warehouse_id") or 1
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

    warehouse = WareHouse.query.filter_by(id=warehouse_id).first()
    if not warehouse:
        return jsonify({"status": False,
            "msg": "WareHouse doesn't exists."
            }), 404

    already_exist = Product.query.filter_by(name=name, warehouse_id=warehouse_id).first()
    if already_exist:
        return jsonify({
            "status": False,
            "msg" : "Product already exist in inventory."
        }), 409


    # Create product and add to database
    new_product = Product(name= name,
                          sku= sku,
                          price= price,
                          category= category if category in categories else "No Category",
                          warehouse_id= warehouse_id)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "status": True,
        "msg": "New product was successfuly created.",
        "data": {"id": new_product.id,
                 "name": new_product.name,
                 "price": new_product.price,
                 "category": new_product.category,
                 "warehouse_id": new_product.warehouse_id},
    }), 201


@bp.get("/products")
@jwt_required()
@require_role('manager', 'admin', 'staff')
def list_products():
    prod = request.args.get("prod")
    category = request.args.get("category")
    warehouse_id = request.args.get("warehouse_id")
    page = max(1, request.args.get("page", default= 1, type= int))
    page_size = min(100, request.args.get("page_size", default=20, type= int))

    query = Product.query

    if prod:
        query = query.filter(Product.name.ilike(f"%{prod}%"))
    if category:
        query = query.filter(Product.category == category)
    if warehouse_id:
        query = query.filter(Product.warehouse_id == warehouse_id)

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
                "warehouse_id": p.warehouse_id,
                "warehouse_name": p.warehouse.name
            }
            for p in items.items
        ]
    }), 200

@bp.get("/products/<int:pid>")
@jwt_required()
def details_product(pid):
    prod = Product.query.filter_by(id=pid).first()

    if not prod:
        return jsonify({"msg" : "No product with that id"}), 401
    return jsonify({"id": prod.id, "sku": prod.sku, "name": prod.name,
                "price": float(prod.price), "category": prod.category}), 200

@bp.patch("/products/<int:pid>")
@jwt_required()
@require_role('manager', 'admin')
def update_product(pid):
    product = Product.query.get_or_404(pid)
    data = request.get_json()

    if "warehouse_id" in data:
        new_wh_id = data.get("warehouse_id")
        if new_wh_id is None:
            return jsonify({"status": False, "msg": "Warehouse id is required."}), 422

        if new_wh_id != product.warehouse_id:
            destination = WareHouse.query.get(new_wh_id)
            if not destination:
                return jsonify({"status": False, "msg": "Warehouse not found."}), 404
            product.warehouse_id = new_wh_id

    if "name" in data:
        product.name = data["name"] or ""
        if not product.name:
            return jsonify({"status": False, "msg": "Name required"})
    if "price" in data:
        product.price = data["price"] or ""
        if not product.price:
            return jsonify({"status": False, "msg": "Price is required"})
    if "category" in data:
        product.category = data["category"] or ""
        if not product.category:
            return jsonify({"status": False, "msg": "Category required"})

    db.session.commit()
    return jsonify({
        "status": True,
        "name": product.name,
        "warehouse_id": product.warehouse_id,
        "price": float(product.price),
        "msg":"Product updated"}), 200

@bp.delete("/products/<int:pid>")
@jwt_required()
@require_role('manager', 'admin')
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    db.session.commit()

    return jsonify({"status":True, "msg":"Product was succesfully deleted."}), 200