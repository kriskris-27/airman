import time

from flask import Blueprint, current_app, jsonify, request

metrics_bp = Blueprint("metrics", __name__)

_VALID_MODES = {"error", "slow", "burst", "normal"}


@metrics_bp.get("/metrics-demo")
def metrics_demo():
    mode = request.args.get("mode", "normal").lower()

    if mode == "error":
        current_app.logger.error("metrics-demo: forced error triggered", extra={"mode": mode})
        return jsonify({"error": "Forced error triggered by ?mode=error"}), 500

    if mode == "slow":
        current_app.logger.info("metrics-demo: slow mode – sleeping 2 s", extra={"mode": mode})
        time.sleep(2)
        return jsonify({"msg": "Slow response completed", "mode": mode}), 200

    if mode == "burst":
        for i in range(1, 6):
            current_app.logger.info(
                f"metrics-demo: burst log line {i}/5",
                extra={"mode": mode, "line": i},
            )
        return jsonify({"msg": "Burst logging complete", "lines_emitted": 5}), 200

    # default / normal
    current_app.logger.info("metrics-demo: normal request", extra={"mode": mode})
    return jsonify({"msg": "OK", "mode": "normal"}), 200
