from flask import Blueprint, jsonify, request
from ..utils.roles import require_role
from flask_jwt_extended import jwt_required
from ..models.product import Product
from .. import db

bp = Blueprint("products", __name__)

categories = {"no category", "category1", "category2", "category3"}

@bp.get("/products")
@jwt_required()
@require_role('manager', 'admin', 'staff')
def list_products():
    prod = request.args.get("prod")
    category = request.args.get("category")
    page = request.args.get("page", default= 1, type= int)
    page_size = request.args.get("page_size", default=20, type= int)

    query = Product.query

    if prod:
        query = query.filter(Product.name.ilike(f"%{prod}"))
    if category:
        query = query.filter(Product.category == category)

    items = query.paginate(page= page, per_page= page_size, error_out=False)

    return jsonify({
        "page": items.page,
        "page_size": items.per_page,
        "total": items.total,
        "products": [
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "price": float(p.price),
                "category": p.category
            }
            for p in items.items
        ]
    }), 200

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
    category = data.get('category') or ""

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

    already_exist = Product.query.filter_by(name=name).first()
    if already_exist:
        return jsonify({
            "status": False,
            "msg" : "Product already exist in inventory."
        }), 409


    # Create product and add to database
    new_product = Product(name= name,
                          sku= sku,
                          price= price,
                          category= category if category in categories else "No Category")
    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "status": True,
        "msg": "New product in your inventory was successfuly added."
    }), 200

@bp.get("/products/<int:pid>")
@jwt_required()
def product_details(pid):
    prod = Product.query.filter_by(id=pid).first()

    if prod:
        return jsonify(            {
                "id": prod.id,
                "sku": prod.sku,
                "name": prod.name,
                "price": float(prod.price),
                "category": prod.category
            })

    return jsonify({"msg" : "No product with that id"}), 401

@bp.put("/products/<int:pid>")
@require_role('manager', 'admin')
@jwt_required()
def update_product(pid):
    product = Product.query.get_or_404(pid)

    data = request.get_json()

    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.category = data.get('category', product.category)

    db.session.commit()
    return jsonify({
        "status": True,
        "msg":"Product updated"}), 200

@bp.delete("/products/<int:pid>")
@require_role('manager', 'admin')
@jwt_required()
def delete_product(pid):
    product = Product.query.get_or_404(pid)

    db.session.delete(product)
    db.session.commit()

    return jsonify(
        {"status":True,
        "msg":"Product was succesfully deleted."}), 200
