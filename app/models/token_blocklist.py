from datetime import datetime, timezone
from .. import db

class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), unique=True, index=True, nullable=False)  # ID unic al tokenului
    token_type = db.Column(db.String(10), nullable=False)  # "access" sau "refresh"
    user_id = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
