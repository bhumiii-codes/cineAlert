import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cinealert-dev-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///cinealert.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONITOR_INTERVAL = 120  # seconds between BMS checks