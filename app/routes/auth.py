from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
            jwt_required, get_jwt_identity,
            create_access_token, create_refresh_token,
            set_access_cookies, set_refresh_cookies
)
from .. import db
from ..models import User

bp = Blueprint("auth", __name__)

@bp.post("/register")
def register():
    data = request.get_json() or {}
    account = data.get("account") or ""
    name = data.get("name") or ""
    email = data.get("email") or ""
    password = data.get("password") or ""

    if not email or not name or not account or not password:
        return jsonify({"error": "email, name, password, account_name required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account already was registered with this email"}), 409

    user = User(email= email, account=account ,name=name)
    user.set_password(raw_password= password)
    db.session.add(user)
    db.session.commit()

    return {"message": "Registered"}, 201

@bp.post("/login")
def login():
    data = request.get_json() or {}
    account = data.get("account") or ""
    password = data.get("password") or ""

    user = User.query.filter_by(account=account).first()

    if not user or not user.check_password(password) or not user.is_active:
        return jsonify({"error": "Invalid account or password"}), 401

    identity = str(user.id)
    claims = {"email": user.email, "name": user.name}
    access = create_access_token(identity=identity, additional_claims=claims)
    refresh = create_refresh_token(identity= identity, additional_claims=claims)

    response = jsonify({"msg": "login successful"})
    set_access_cookies(response, access)
    set_refresh_cookies(response, refresh)
    return response, 200

@bp.get("/me")
@jwt_required()
def me():
    return jsonify({"user": get_jwt_identity()})