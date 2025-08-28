from flask import Blueprint

def register_blueprints(app):
    from .auth import bp as auth
    app.register_blueprint(auth, url_prefix="/auth")

    from .demo_routes import bp as test_routes
    app.register_blueprint(test_routes, url_prefix="/demo")

    from .products import bp as products
    app.register_blueprint(products)
    return app