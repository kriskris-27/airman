import os
from flask import Flask

from app.logger import setup_logger
from app.db import init_db
from app.routes.health import health_bp
from app.routes.events import events_bp
from app.routes.metrics import metrics_bp


def create_app():
    app = Flask(__name__)

    # Config from environment
    app.config["APP_ENV"] = os.environ.get("APP_ENV", "development")
    app.config["LOG_LEVEL"] = os.environ.get("LOG_LEVEL", "INFO")
    app.config["STORE_BACKEND"] = os.environ.get("STORE_BACKEND", "sqlite")
    app.config["SQLITE_PATH"] = os.environ.get("SQLITE_PATH", "./data/events.db")
    app.config["SERVICE_NAME"] = os.environ.get("SERVICE_NAME", "skynet-ops-audit-service")

    # Set up structured JSON logger
    setup_logger(app)

    # Initialise database (creates table if needed)
    init_db(app)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(metrics_bp)

    return app
