from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": current_app.config["SERVICE_NAME"],
            "environment": current_app.config["APP_ENV"],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        }
    ), 200
