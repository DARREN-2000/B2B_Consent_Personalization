"""Health check API blueprint."""

from flask import Blueprint, jsonify
from datetime import datetime, timezone
from app import db


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"

    return jsonify({
        "status": "healthy" if db_status == "ok" else "degraded",
        "timestamp": _utcnow().isoformat(),
        "version": "1.0.0",
        "database": db_status,
    })
