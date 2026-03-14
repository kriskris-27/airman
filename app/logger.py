import logging
from pythonjsonlogger import jsonlogger


class _CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Renames the default 'message' key to 'msg' and ensures
    level + timestamp are always present.
    """

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        # Normalise field names
        log_record["level"] = record.levelname
        log_record["msg"] = log_record.pop("message", record.getMessage())
        # 'timestamp' is already emitted by the base formatter via %(asctime)s
        if "asctime" in log_record:
            log_record["timestamp"] = log_record.pop("asctime")


def setup_logger(app):
    """Attach a structured JSON handler to the Flask app logger."""
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

    handler = logging.StreamHandler()
    formatter = _CustomJsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    app.logger.propagate = False

    app.logger.info(
        "Logger initialised",
        extra={"service": app.config.get("SERVICE_NAME"), "env": app.config.get("APP_ENV")},
    )
