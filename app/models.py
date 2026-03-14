import uuid
from datetime import datetime, timezone


def generate_event_id() -> str:
    """Return a new UUID4 string to serve as the event identifier."""
    return str(uuid.uuid4())


def get_stored_at() -> str:
    """Return the current UTC time formatted as an ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
