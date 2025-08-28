from flask import Blueprint, jsonify
from ..utils.roles import require_role
from flask_jwt_extended import jwt_required

bp = Blueprint("demo", __name__)

@bp.get("/ping")
@jwt_required()
def ping():
    return jsonify({"msg": "Access Succesfully"})

@bp.get("/admin-only")
@require_role("admin")
def admin_only():
    return jsonify({"msg": "Admin"})

@bp.get("/manager-or-admin")
@require_role("manager", "admin")
def manager_or_admin():
    return jsonify({"msg": "salut manager/admin"})
