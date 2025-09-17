from datetime import datetime
from sqlalchemy import Index
from .. import db

def time_now():
    return datetime.now()

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, index=True, nullable=False)
    name = db.Column(db.String(200), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False, default="No category")
    created_at = db.Column(db.DateTime, default=time_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=time_now, onupdate=time_now, nullable=False)

    stock_items = db.relationship("Stock", back_populates="product", passive_deletes=True, lazy="selectin")
    stock_movements = db.relationship("StockMovement", back_populates="product")
    transfer_items = db.relationship("TransferItem", back_populates="product")


    __table_args__ = (
        Index("ix_products_name", "name"),
        Index("ix_products_category", "category"),
    )
