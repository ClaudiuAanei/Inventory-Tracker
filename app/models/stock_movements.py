from datetime import datetime
from sqlalchemy import ForeignKey
from .. import db

def time_now():
    return datetime.now()

class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum("IN", "OUT", "ADJUST_ABS", "ADJUST_REL",
                             name="stockmovement_type"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(100), nullable=True)

    # ForeignKey's
    actor_user_id = db.Column(db.Integer, ForeignKey("users.id"), index=True, nullable=False)
    product_id = db.Column(db.Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, ForeignKey("warehouse.id"), nullable=False, index=True)
    related_transfer_id = db.Column(db.Integer, ForeignKey("transfers.id"), index=True, nullable=True)

    #Time
    created_at = db.Column(db.DateTime, nullable=False, default=time_now, index=True)

    actor_user = db.relationship("User", back_populates="stock_movements")
    warehouse = db.relationship("WareHouse", back_populates="stock_movements")
    product = db.relationship("Product", back_populates="stock_movements")
    transfer = db.relationship("Transfer", back_populates="stock_movements")
