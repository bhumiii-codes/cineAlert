from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, User, Alert, SeenShow
from monitor import start_monitor_thread, send_telegram
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# ── PUT YOUR TELEGRAM BOT TOKEN HERE ─────────────────────────────────────────
app.config["TELEGRAM_BOT_TOKEN"] = "8271870254:AAGha4897Y5PHLpaBEpum-hCNn25xS3zSzs"

CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()
    print("✅ Database ready")

# Start background monitor
start_monitor_thread(app, interval=app.config["MONITOR_INTERVAL"])
print("✅ Monitor thread started")


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "CineAlert API is running 🎬"})


# -- Users --

@app.route("/users", methods=["POST"])
def register_user():
    """Register a new user with their Telegram ID."""
    data = request.get_json()
    telegram_id = data.get("telegram_id", "").strip()
    name        = data.get("name", "").strip()

    if not telegram_id:
        return jsonify({"error": "telegram_id is required"}), 400

    existing = User.query.filter_by(telegram_id=telegram_id).first()
    if existing:
        return jsonify({"message": "User already exists", "user": existing.to_dict()}), 200

    user = User(telegram_id=telegram_id, name=name)
    db.session.add(user)
    db.session.commit()

    # Welcome message
    token = app.config["TELEGRAM_BOT_TOKEN"]
    send_telegram(token, telegram_id,
        f"👋 Welcome to <b>CineAlert</b>, {name}!\n\n"
        "You'll get instant Telegram alerts whenever a new show matches your preferences.\n\n"
        "Set up your first alert on the CineAlert website. 🎬"
    )

    return jsonify({"message": "User registered", "user": user.to_dict()}), 201


@app.route("/users/<telegram_id>", methods=["GET"])
def get_user(telegram_id):
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())


# -- Alerts --

@app.route("/alerts", methods=["POST"])
def create_alert():
    """Create a new alert for a user."""
    data        = request.get_json()
    telegram_id = data.get("telegram_id", "").strip()
    movie_name  = data.get("movie_name", "").strip()
    city        = data.get("city", "").strip()
    fmt         = data.get("format", "ANY").strip().upper()
    pref_time   = data.get("preferred_time", "ANY").strip().upper()
    venue       = data.get("venue", "ANY").strip()

    if not telegram_id or not movie_name or not city:
        return jsonify({"error": "telegram_id, movie_name, and city are required"}), 400

    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return jsonify({"error": "User not found. Register first."}), 404

    alert = Alert(
        user_id=user.id,
        movie_name=movie_name,
        city=city,
        format=fmt,
        preferred_time=pref_time,
        venue=venue,
    )
    db.session.add(alert)
    db.session.commit()

    # Confirm to user on Telegram
    token = app.config["TELEGRAM_BOT_TOKEN"]
    send_telegram(token, telegram_id,
        f"✅ <b>Alert created!</b>\n\n"
        f"🎬 {movie_name}\n"
        f"📍 {city}\n"
        f"📺 {fmt}\n"
        f"🕐 {pref_time}\n"
        f"🏟 {venue}\n\n"
        "I'll ping you the moment a matching show appears on BookMyShow!"
    )

    return jsonify({"message": "Alert created", "alert": alert.to_dict()}), 201


@app.route("/alerts/<telegram_id>", methods=["GET"])
def get_alerts(telegram_id):
    """Get all alerts for a user."""
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"alerts": [a.to_dict() for a in user.alerts]})


@app.route("/alerts/<int:alert_id>", methods=["DELETE"])
def delete_alert(alert_id):
    """Delete an alert by ID."""
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404
    db.session.delete(alert)
    db.session.commit()
    return jsonify({"message": "Alert deleted"})


@app.route("/alerts/<int:alert_id>/toggle", methods=["PATCH"])
def toggle_alert(alert_id):
    """Pause or resume an alert."""
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404
    alert.is_active = not alert.is_active
    db.session.commit()
    status = "active" if alert.is_active else "paused"
    return jsonify({"message": f"Alert {status}", "alert": alert.to_dict()})


# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)