import json

from flask import Blueprint, current_app, jsonify, request

from app.db import get_db
from app.models import generate_event_id, get_stored_at

events_bp = Blueprint("events", __name__)

_VALID_SEVERITIES = {"info", "warning", "error", "critical"}
_REQUIRED_FIELDS = {"type", "tenantId", "severity", "message", "source"}


# ---------------------------------------------------------------------------
# POST /events
# ---------------------------------------------------------------------------
@events_bp.post("/events")
def create_event():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # Validate required fields
    missing = _REQUIRED_FIELDS - set(body.keys())
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(sorted(missing))}"}), 400

    severity = body["severity"].lower()
    if severity not in _VALID_SEVERITIES:
        return jsonify(
            {"error": f"severity must be one of: {', '.join(sorted(_VALID_SEVERITIES))}"}
        ), 400

    # Serialize optional metadata
    metadata = body.get("metadata")
    metadata_str = json.dumps(metadata) if metadata is not None else None

    event_id = generate_event_id()
    stored_at = get_stored_at()

    db = get_db(current_app)
    db.execute(
        """
        INSERT INTO events
            (event_id, type, tenant_id, severity, message, source,
             metadata, occurred_at, trace_id, stored_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            body["type"],
            body["tenantId"],
            severity,
            body["message"],
            body["source"],
            metadata_str,
            body.get("occurredAt"),
            body.get("traceId"),
            stored_at,
        ),
    )
    db.commit()

    current_app.logger.info(
        "Event stored",
        extra={
            "eventId": event_id,
            "tenantId": body["tenantId"],
            "severity": severity,
            "type": body["type"],
        },
    )

    return jsonify({"success": True, "eventId": event_id, "storedAt": stored_at}), 201


# ---------------------------------------------------------------------------
# GET /events
# ---------------------------------------------------------------------------
@events_bp.get("/events")
def list_events():
    tenant_id = request.args.get("tenantId")
    severity = request.args.get("severity")
    event_type = request.args.get("type")

    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except ValueError:
        return jsonify({"error": "limit and offset must be integers"}), 400

    # Build dynamic WHERE clause
    conditions = []
    params = []

    if tenant_id:
        conditions.append("tenant_id = ?")
        params.append(tenant_id)
    if severity:
        if severity.lower() not in _VALID_SEVERITIES:
            return jsonify(
                {"error": f"severity must be one of: {', '.join(sorted(_VALID_SEVERITIES))}"}
            ), 400
        conditions.append("severity = ?")
        params.append(severity.lower())
    if event_type:
        conditions.append("type = ?")
        params.append(event_type)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    db = get_db(current_app)

    total_row = db.execute(f"SELECT COUNT(*) FROM events {where}", params).fetchone()
    total = total_row[0]

    rows = db.execute(
        f"""
        SELECT event_id, type, tenant_id, severity, message, source,
               metadata, occurred_at, trace_id, stored_at
        FROM events
        {where}
        ORDER BY stored_at DESC
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset],
    ).fetchall()

    items = []
    for row in rows:
        item = dict(row)
        # Rename snake_case keys to camelCase for API consistency
        item["eventId"] = item.pop("event_id")
        item["tenantId"] = item.pop("tenant_id")
        item["occurredAt"] = item.pop("occurred_at")
        item["traceId"] = item.pop("trace_id")
        item["storedAt"] = item.pop("stored_at")
        # Deserialise metadata back to object if present
        if item["metadata"]:
            try:
                item["metadata"] = json.loads(item["metadata"])
            except (json.JSONDecodeError, TypeError):
                pass
        items.append(item)

    return jsonify({"items": items, "total": total, "limit": limit, "offset": offset}), 200
