from flask import Blueprint

def register_blueprints(app):
    from .auth import bp as auth
    app.register_blueprint(auth, url_prefix="/auth")
    return app