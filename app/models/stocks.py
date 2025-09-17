from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint, Index
from .. import db

def time_now():
    return datetime.now()

class Stock(db.Model):
    __tablename__ = "stocks"

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, ForeignKey("warehouse.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id   = db.Column(db.Integer, ForeignKey("products.id",  ondelete="RESTRICT"), nullable=False, index=True)
    quantity     = db.Column(db.Integer, nullable=False, default=0)
    min_threshold = db.Column(db.Integer, nullable=False, default=0)
    max_capacity  = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=time_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=time_now, onupdate=time_now)

    warehouse = db.relationship("WareHouse", back_populates="stock_items", lazy="selectin")
    product   = db.relationship("Product",  back_populates="stock_items", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("warehouse_id", "product_id", name="uq_stock_prod_wh"),
        CheckConstraint("quantity >= 0", name="ck_stock_quantity_nonneg"),
        CheckConstraint("min_threshold >= 0", name="ck_stock_min_threshold_nonneg"),
        Index("ix_stock_prod_wh", "product_id", "warehouse_id"),
    )
