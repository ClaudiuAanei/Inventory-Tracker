from datetime import datetime
from .. import db

def time_now():
    return datetime.now()

class WareHouse(db.Model):
    __tablename__ = "warehouse"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True, index=True)
    location = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=time_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=time_now, onupdate=time_now)

    stock_items = db.relationship("Stock", back_populates="warehouse", passive_deletes=True, lazy="selectin")
    stock_movements = db.relationship("StockMovement", back_populates="warehouse")

    outgoing_transfers = db.relationship("Transfer", back_populates="source_warehouse", foreign_keys="Transfer.source_warehouse_id")
    incoming_transfers = db.relationship("Transfer", back_populates="dest_warehouse", foreign_keys="Transfer.dest_warehouse_id")

    products = db.relationship(
        "Product",
        secondary="stocks",
        primaryjoin="WareHouse.id == Stock.warehouse_id",
        secondaryjoin="Product.id == Stock.product_id",
        viewonly=True,
        lazy="selectin",
    )
