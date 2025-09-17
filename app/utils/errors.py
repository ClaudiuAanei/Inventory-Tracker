from flask import jsonify
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager
from .. import db


def register_jwt_errors(jwt: JWTManager):
    @jwt.unauthorized_loader
    def custom_unauthorized_response(err_str):
        return jsonify({"error": "You must be logged in to access this route"}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token(err_str):
        return jsonify({"error": "Invalid token, please log in again"}), 401

    @jwt.expired_token_loader
    def custom_expired_token(jwt_header, jwt_payload):
        return jsonify({"error": "Token expired, please log in again"}), 401

    @jwt.revoked_token_loader
    def custom_revoked_token(jwt_header, jwt_payload):
        return jsonify({"error": "This token has been revoked"}), 401