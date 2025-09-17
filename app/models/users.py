from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    account = db.Column(db.String(255), unique=True, index=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="staff")
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)


    # Relationships
    stock_movements = db.relationship("StockMovement", back_populates="actor_user")
    created_transfers = db.relationship("Transfer", back_populates="created_by_user", foreign_keys="Transfer.created_by_user_id")
    source_confirmed_transfers = db.relationship("Transfer", back_populates="confirmed_by_source", foreign_keys="Transfer.confirmed_by_source_user_id")
    dest_confirmed_transfers = db.relationship("Transfer", back_populates="confirmed_by_dest", foreign_keys="Transfer.confirmed_by_dest_user_id")


    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)