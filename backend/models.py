from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    telegram_id   = db.Column(db.String(50), unique=True, nullable=False)
    name          = db.Column(db.String(100))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    alerts        = db.relationship("Alert", backref="user", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "alerts": [a.to_dict() for a in self.alerts]
        }


class Alert(db.Model):
    __tablename__ = "alerts"

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    movie_name    = db.Column(db.String(200), nullable=False)
    city          = db.Column(db.String(100), nullable=False)
    format        = db.Column(db.String(20), nullable=False)   # IMAX / 3D / 2D / ANY
    preferred_time= db.Column(db.String(20), default="ANY")    # MORNING / AFTERNOON / EVENING / NIGHT / ANY
    venue         = db.Column(db.String(200), default="ANY")   # specific venue or ANY

    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked  = db.Column(db.DateTime)
    last_triggered= db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "movie_name": self.movie_name,
            "city": self.city,
            "format": self.format,
            "preferred_time": self.preferred_time,
            "venue": self.venue,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None
        }


class SeenShow(db.Model):
    """Tracks shows we've already alerted for, per alert."""
    __tablename__ = "seen_shows"

    id       = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("alerts.id"), nullable=False)
    show_hash= db.Column(db.String(64), nullable=False)
    seen_at  = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("alert_id", "show_hash"),)