from datetime import datetime
from .. import db

def time_now():
    return datetime.now()

class WareHouse(db.Model):
    __tablename__ = "warehouse"
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(30), nullable= False, unique= True)
    location = db.Column(db.String(200), nullable= False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=time_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=time_now, onupdate=time_now)

    # One depozit can have products
    products = db.relationship(
        "Product",
        back_populates="warehouse",
        passive_deletes=True,
    )
