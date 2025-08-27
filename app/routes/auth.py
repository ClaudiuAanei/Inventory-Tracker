from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
            jwt_required, get_jwt_identity, get_jwt,
            create_access_token, create_refresh_token,
            set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)
from .. import db
from ..models import User, TokenBlocklist

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
    claims = {"email": user.email, "name": user.name, "account": user.role}
    access_token = create_access_token(identity=identity, additional_claims=claims)
    refresh_token = create_refresh_token(identity= identity, additional_claims=claims)

    response = jsonify({"msg": "login successful"})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200

@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    claims = get_jwt()
    uid = get_jwt_identity()

    db.session.add(TokenBlocklist(jti=claims["jti"], token_type="refresh", user_id=int(uid)))

    user = User.query.get(int(uid))
    claims = {"email": user.email, "name": user.name, "role": user.role}

    new_access = create_access_token(identity=uid, additional_claims=claims)
    new_refresh = create_refresh_token(identity=uid, additional_claims=claims)

    response = jsonify({"msg": "Refreshed"})
    try:
        set_access_cookies(response, new_access)
        set_refresh_cookies(response, new_refresh)
    except Exception:
        pass

    db.session.commit()
    return response, 200


@bp.post("/logout")
@jwt_required(verify_type=False)  # acceptă access sau refresh
def logout():
    """Revocă tokenul curent și șterge cookies (dacă există)."""
    jwt_data = get_jwt()
    uid = int(get_jwt_identity())
    jti = jwt_data["jti"]
    ttype = jwt_data["type"]

    db.session.add(TokenBlocklist(jti=jti, token_type=ttype, user_id=uid))
    db.session.commit()

    resp = jsonify({"msg": "logged out"})
    try:
        unset_jwt_cookies(resp)
    except Exception:
        pass
    return resp, 200

@bp.get("/me")
@jwt_required()
def me():
    identity = get_jwt_identity()
    claims = get_jwt()
    return jsonify({"user": identity,
                    "account": claims.get('account')})