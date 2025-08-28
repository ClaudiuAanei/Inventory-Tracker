from datetime import datetime, timezone, timedelta
from app.models import TokenBlocklist
from app import db, create_app

def cleanup_old_tokens(hours=6):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    deleted = TokenBlocklist.query.filter(TokenBlocklist.created_at < cutoff).delete()
    db.session.commit()
    return deleted

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        deleted = cleanup_old_tokens(hours=6)  # modifică după nevoie
        print(f"[{datetime.now().isoformat()}] Deleted {deleted} old tokens")