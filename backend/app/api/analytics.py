"""Analytics API blueprint — aggregate statistics over consent records."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app import db
from app.models import ConsentRecord, ConsentPolicy, Organization, User
from app.utils import require_role

analytics_bp = Blueprint("analytics", __name__)


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@analytics_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """High-level consent statistics."""
    claims = get_jwt()
    org_id = claims.get("organization_id")

    # Counts by status
    q = db.session.query(ConsentRecord.status, func.count(ConsentRecord.id))
    if claims.get("role") != "admin":
        q = q.filter(ConsentRecord.organization_id == org_id)
    status_counts = dict(q.group_by(ConsentRecord.status).all())

    total = sum(status_counts.values())
    granted = status_counts.get("granted", 0)
    consent_rate = round((granted / total * 100), 2) if total else 0

    # Counts by policy
    q2 = db.session.query(ConsentRecord.policy_id, func.count(ConsentRecord.id))
    if claims.get("role") != "admin":
        q2 = q2.filter(ConsentRecord.organization_id == org_id)
    policy_counts = dict(q2.group_by(ConsentRecord.policy_id).all())

    # Counts by method
    q3 = db.session.query(ConsentRecord.consent_method, func.count(ConsentRecord.id))
    if claims.get("role") != "admin":
        q3 = q3.filter(ConsentRecord.organization_id == org_id)
    method_counts = dict(q3.group_by(ConsentRecord.consent_method).all())

    return jsonify({
        "total_records": total,
        "consent_rate_pct": consent_rate,
        "by_status": status_counts,
        "by_method": method_counts,
        "by_policy": policy_counts,
    }), 200


@analytics_bp.route("/trends", methods=["GET"])
@jwt_required()
def trends():
    """Daily consent grant/denial trends for the last N days."""
    claims = get_jwt()
    org_id = claims.get("organization_id")
    days = request.args.get("days", 30, type=int)

    cutoff = _utcnow() - timedelta(days=days)

    query = (
        db.session.query(
            func.date(ConsentRecord.created_at).label("date"),
            ConsentRecord.status,
            func.count(ConsentRecord.id).label("count"),
        )
        .filter(ConsentRecord.created_at >= cutoff)
    )
    if claims.get("role") != "admin":
        query = query.filter(ConsentRecord.organization_id == org_id)

    rows = query.group_by(func.date(ConsentRecord.created_at), ConsentRecord.status).all()

    result = {}
    for row in rows:
        date_str = str(row.date)
        if date_str not in result:
            result[date_str] = {}
        result[date_str][row.status] = row.count

    sorted_result = [{"date": k, **v} for k, v in sorted(result.items())]

    return jsonify({"days": days, "trends": sorted_result}), 200


@analytics_bp.route("/overview", methods=["GET"])
@jwt_required()
@require_role("admin")
def platform_overview():
    """Platform-wide overview (admin only)."""
    total_orgs = Organization.query.count()
    active_orgs = Organization.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_policies = ConsentPolicy.query.count()
    total_records = ConsentRecord.query.count()

    return jsonify({
        "organizations": {"total": total_orgs, "active": active_orgs},
        "users": {"total": total_users},
        "policies": {"total": total_policies},
        "consent_records": {"total": total_records},
    }), 200
