import requests
import hashlib
import threading
import time
from datetime import datetime

# ── BMS CONFIG ───────────────────────────────────────────────────────────────
BMS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://in.bookmyshow.com/",
}

CITY_CODES = {
    "chennai":  "CHEN",
    "mumbai":   "MUMBAI",
    "delhi":    "NCR",
    "bangalore": "BANG",
    "hyderabad": "HYD",
    "pune":     "PUNE",
    "kolkata":  "KOLK",
}

TIME_SLOTS = {
    "MORNING":   (0,  12),
    "AFTERNOON": (12, 16),
    "EVENING":   (16, 20),
    "NIGHT":     (20, 24),
    "ANY":       (0,  24),
}

# ── TELEGRAM ─────────────────────────────────────────────────────────────────
def send_telegram(token: str, chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"Telegram error for {chat_id}: {e}")
        return False


# ── BMS FETCH ─────────────────────────────────────────────────────────────────
def fetch_shows(movie_name: str, city: str, fmt: str):
    """
    Searches BMS for shows matching movie + city + format.
    Returns list of dicts: {hash, venue, date, time, dimension, booking_url}
    """
    city_code = CITY_CODES.get(city.lower(), city.upper())
    results = []

    try:
        # Step 1: search for the movie event code
        search_url = "https://in.bookmyshow.com/api/movies-data/search"
        search_resp = requests.get(search_url, params={
            "appCode": "MOBAND2",
            "appVersion": "14.5",
            "language": "en",
            "searchString": movie_name,
            "regionCode": city_code,
        }, headers=BMS_HEADERS, timeout=15)

        if search_resp.status_code != 200:
            return results

        search_data = search_resp.json()
        events = search_data.get("BookMyShow", {}).get("arrEvents", [])

        event_code = None
        movie_slug = ""
        for event in events:
            if movie_name.lower() in event.get("EventTitle", "").lower():
                event_code = event.get("EventCode")
                movie_slug = event.get("EventTitle", "").lower().replace(" ", "-")
                break

        if not event_code:
            return results

        # Step 2: fetch showtimes for this event
        shows_url = "https://in.bookmyshow.com/api/movies-data/showtimes-by-event"
        shows_resp = requests.get(shows_url, params={
            "appCode": "MOBAND2",
            "appVersion": "14.5",
            "language": "en",
            "eventCode": event_code,
            "regionCode": city_code,
            "bmsId": "1.21.5",
            "token": "67x1xa33b4x422b361ba",
        }, headers={**BMS_HEADERS, "x-region-code": city_code}, timeout=15)

        if shows_resp.status_code != 200:
            return results

        data = shows_resp.json()
        venue_list = data.get("BookMyShow", {}).get("arrEvents", [])

        booking_base = f"https://in.bookmyshow.com/buytickets/{movie_slug}/movie-{city.lower()}-{event_code}-MT/"

        for venue_data in venue_list:
            venue_name = venue_data.get("venueName", venue_data.get("sVenueName", ""))
            show_dates = venue_data.get("arrShowDetails", venue_data.get("arrShowData", []))

            for day in show_dates:
                show_date = day.get("sDate", day.get("date", ""))
                for show in day.get("arrShowTime", day.get("arrShows", [])):
                    show_time  = show.get("sShowTime", show.get("sTime", ""))
                    dimension  = show.get("sDimension", show.get("sSubTitle", ""))

                    # Format filter
                    if fmt != "ANY":
                        if fmt.lower() not in dimension.lower() and fmt.lower() not in venue_name.lower():
                            continue

                    show_hash = hashlib.md5(
                        f"{venue_name}{show_date}{show_time}{dimension}".encode()
                    ).hexdigest()

                    results.append({
                        "hash":        show_hash,
                        "venue":       venue_name,
                        "date":        show_date,
                        "time":        show_time,
                        "dimension":   dimension,
                        "booking_url": booking_base,
                    })

    except Exception as e:
        print(f"BMS fetch error: {e}")

    return results


def matches_time_preference(show_time: str, preference: str) -> bool:
    if preference == "ANY":
        return True
    try:
        # show_time format: "10:30 AM" or "22:30"
        t = datetime.strptime(show_time.strip(), "%I:%M %p")
        hour = t.hour
    except:
        try:
            t = datetime.strptime(show_time.strip(), "%H:%M")
            hour = t.hour
        except:
            return True  # can't parse, allow it

    start, end = TIME_SLOTS.get(preference, (0, 24))
    return start <= hour < end


# ── MONITOR LOOP ──────────────────────────────────────────────────────────────
def run_monitor(app, interval: int = 120):
    """Runs in a background thread. Checks all active alerts every `interval` seconds."""
    from models import Alert, SeenShow, User, db

    print(f"[Monitor] Started — checking every {interval}s")

    while True:
        try:
            with app.app_context():
                alerts = Alert.query.filter_by(is_active=True).all()
                print(f"[Monitor] Checking {len(alerts)} active alert(s)...")

                for alert in alerts:
                    shows = fetch_shows(alert.movie_name, alert.city, alert.format)

                    for show in shows:
                        # Skip time mismatch
                        if not matches_time_preference(show["time"], alert.preferred_time):
                            continue

                        # Skip venue mismatch
                        if alert.venue != "ANY" and alert.venue.lower() not in show["venue"].lower():
                            continue

                        # Skip already seen
                        already_seen = SeenShow.query.filter_by(
                            alert_id=alert.id, show_hash=show["hash"]
                        ).first()
                        if already_seen:
                            continue

                        # New show! Alert the user
                        user = User.query.get(alert.user_id)
                        if user:
                            msg = (
                                f"🚨 <b>NEW SHOW FOUND!</b>\n\n"
                                f"🎬 <b>{alert.movie_name}</b>\n"
                                f"🏟 {show['venue']}\n"
                                f"📅 {show['date']}  🕐 {show['time']}\n"
                                f"📺 {show['dimension']}\n\n"
                                f"👉 <a href='{show['booking_url']}'>BOOK NOW on BookMyShow</a>\n\n"
                                f"⚡ Seats fill fast — go go go!"
                            )
                            # Use the app's telegram token from config
                            from flask import current_app
                            token = current_app.config.get("TELEGRAM_BOT_TOKEN", "")
                            send_telegram(token, user.telegram_id, msg)

                        # Mark as seen
                        seen = SeenShow(alert_id=alert.id, show_hash=show["hash"])
                        db.session.add(seen)

                    # Update last_checked
                    alert.last_checked = datetime.utcnow()

                db.session.commit()

        except Exception as e:
            print(f"[Monitor] Error: {e}")

        time.sleep(interval)


def start_monitor_thread(app, interval: int = 120):
    t = threading.Thread(target=run_monitor, args=(app, interval), daemon=True)
    t.start()
    return t