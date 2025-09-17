import os
import dotenv
from datetime import timedelta
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
dotenv.load_dotenv()

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
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
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = False  # True în producție (doar HTTPS)
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # pentru protecție CSRF
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"

    # init DataBase, Migrate and JWT
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from .models.token_blocklist import TokenBlocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload.get("jti")
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None

    from .utils.errors import register_jwt_errors
    register_jwt_errors(jwt)

    # Blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        # activează FK enforcement doar pentru SQLite
        if isinstance(dbapi_connection, SQLite3Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()


    # TEST
    @app.get("/")
    def home():
        return jsonify(name="Inventory Tracker App", status="Ready")

    return app
