from .. import db
from sqlalchemy import ForeignKey
from datetime import datetime as dt

def time_now():
    return dt.now()

class Transfer(db.Model):
    __tablename__ = "transfers"
    id = db.Column(db.Integer, primary_key= True)
    status = db.Column(db.Enum("PENDING", "READY_TO_DELIVER", "IN_TRANSIT", "DELIVERED", "RECEIVED",
                               name="transfer_status"), nullable=False, index=True)

    # ForeignKeys
    source_warehouse_id = db.Column(db.Integer, ForeignKey("warehouse.id"), nullable=False, index=True)
    dest_warehouse_id = db.Column(db.Integer, ForeignKey("warehouse.id"), nullable=False, index=True)
    created_by_user_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=False, index=True)
    confirmed_by_source_user_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=True, index=True)
    confirmed_by_dest_user_id = db.Column(db.Integer, ForeignKey("users.id"), nullable= True, index=True)

    notes = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=time_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=time_now, onupdate= time_now)

    # Relationships
    stock_movements = db.relationship("StockMovement", back_populates="transfer")
    source_warehouse = db.relationship("WareHouse", foreign_keys=[source_warehouse_id], back_populates="outgoing_transfers")
    dest_warehouse = db.relationship("WareHouse", foreign_keys=[dest_warehouse_id], back_populates="incoming_transfers")

    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id], back_populates="created_transfers")
    confirmed_by_source = db.relationship("User", foreign_keys=[confirmed_by_source_user_id],
                                          back_populates="source_confirmed_transfers")
    confirmed_by_dest = db.relationship("User", foreign_keys=[confirmed_by_dest_user_id],
                                        back_populates="dest_confirmed_transfers")

    items = db.relationship("TransferItem",back_populates="transfer",cascade="all, delete-orphan",lazy="selectin")

    __table_args__ = (
        db.CheckConstraint("source_warehouse_id <> dest_warehouse_id", name="ck_transfer_src_ne_dest"),
    )