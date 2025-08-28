from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify

def require_role(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role", "staff")
            if role not in allowed_roles:
                return jsonify({"error": "forbidden – You are not allowed!"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
