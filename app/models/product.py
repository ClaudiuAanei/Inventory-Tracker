from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint, Index
from .. import db

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, index=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False, default="No category")
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    warehouse_id = db.Column(db.Integer, ForeignKey("warehouse.id", ondelete="RESTRICT"),
                             nullable=False, index=True)

    # Many-to-one relationship products -> WearHouse
    warehouse = db.relationship("WareHouse", back_populates="products", passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("warehouse_id", "name", name="uq_products_wh_name"),  # opțional
        Index("ix_products_wh_name", "warehouse_id", "name"),
    )