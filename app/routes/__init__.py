from flask import Blueprint

def register_blueprints(app):

    # Login System
    from .auth import bp as auth
    app.register_blueprint(auth, url_prefix="/auth")

    # Admin Decorator Tests
    from .demo_routes import bp as test_routes
    app.register_blueprint(test_routes, url_prefix="/demo")

    # Products
    from .products import bp as products
    app.register_blueprint(products)

    # WareHouse
    from .warehouses import bp as warehouses
    app.register_blueprint(warehouses)

    from .stocks import bp as stocks
    app.register_blueprint(stocks)

    from .stock_movement import bp as stock_movement
    app.register_blueprint(stock_movement)


    return app