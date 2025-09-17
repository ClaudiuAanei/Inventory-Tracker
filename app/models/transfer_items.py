from datetime import datetime as dt
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from .. import db

def time_now():
    return dt.now()

class TransferItem(db.Model):
    __tablename__ = "transfer_items"

    id = db.Column(db.Integer, primary_key=True)

    transfer_id = db.Column(db.Integer,ForeignKey("transfers.id", ondelete="CASCADE"),nullable=False,index=True)
    product_id = db.Column(db.Integer,ForeignKey("products.id"),nullable=False,index=True)

    quantity   = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=time_now)

    transfer = db.relationship("Transfer", back_populates="items")
    product  = db.relationship("Product",  back_populates="transfer_items")

    __table_args__ = (
        UniqueConstraint("transfer_id", "product_id", name="uq_transfer_item_per_product"),
        CheckConstraint("quantity > 0", name="ck_transfer_item_qty_pos"),
    )

    def __repr__(self):
        return f"<TransferItem transfer={self.transfer_id} product={self.product_id} qty={self.quantity}>"
