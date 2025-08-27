import os
import dotenv
from datetime import timedelta
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

dotenv.load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():

    app = Flask(__name__)

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///inventory.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "THIS PASSWORD MUST BE CHANGE LATER IN PRODUCTION")

    # Token Lifetime
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=20)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=14)
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False  # True în producție (doar HTTPS)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True  # pentru protecție CSRF
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"

    # init DataBase, Migrate and JWT
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # TEST
    # @app.get("/")
    # def home():
    #     return jsonify(name="Inventory Tracker App", status="Ready")

    return app