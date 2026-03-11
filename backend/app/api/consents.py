"""Consent Management API blueprint.

Endpoints:
  POST   /api/consents/policies              - Create consent policy
  GET    /api/consents/policies              - List consent policies
  GET    /api/consents/policies/<id>         - Get policy
  PUT    /api/consents/policies/<id>         - Update policy
  DELETE /api/consents/policies/<id>         - Delete policy

  POST   /api/consents/records               - Record a consent decision
  GET    /api/consents/records               - List records (filterable)
  GET    /api/consents/records/<id>          - Get single record
  PUT    /api/consents/records/<id>/withdraw - Withdraw consent
  GET    /api/consents/records/export        - Export records (csv/json)
"""

import json
import csv
from io import BytesIO, StringIO
from datetime import datetime, timedelta, timezone


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app import db
from app.models import ConsentPolicy, ConsentRecord
from app.utils import require_role, paginate

consents_bp = Blueprint("consents", __name__)

# ─── Policies ────────────────────────────────────────────────────────────────

@consents_bp.route("/policies", methods=["POST"])
@jwt_required()
@require_role("admin", "editor")
def create_policy():
    data = request.get_json(silent=True) or {}
    required = ["name", "policy_type"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    claims = get_jwt()
    policy = ConsentPolicy(
        organization_id=data.get("organization_id") or claims["organization_id"],
        name=data["name"],
        description=data.get("description"),
        policy_type=data["policy_type"],
        version=data.get("version", "1.0"),
        requires_explicit_consent=data.get("requires_explicit_consent", True),
        retention_days=data.get("retention_days", 365),
    )
    db.session.add(policy)
    db.session.commit()
    return jsonify(policy.to_dict()), 201


@consents_bp.route("/policies", methods=["GET"])
@jwt_required()
def list_policies():
    claims = get_jwt()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = ConsentPolicy.query
    if claims.get("role") != "admin":
        query = query.filter_by(organization_id=claims["organization_id"])

    org_id = request.args.get("organization_id")
    if org_id and claims.get("role") == "admin":
        query = query.filter_by(organization_id=org_id)

    policy_type = request.args.get("policy_type")
    if policy_type:
        query = query.filter_by(policy_type=policy_type)

    is_active = request.args.get("is_active")
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == "true")

    query = query.order_by(ConsentPolicy.created_at.desc())
    return jsonify(paginate(query, page, per_page)), 200


@consents_bp.route("/policies/<policy_id>", methods=["GET"])
@jwt_required()
def get_policy(policy_id):
    claims = get_jwt()
    policy = ConsentPolicy.query.get_or_404(policy_id)
    if claims.get("role") != "admin" and policy.organization_id != claims["organization_id"]:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(policy.to_dict()), 200


@consents_bp.route("/policies/<policy_id>", methods=["PUT"])
@jwt_required()
@require_role("admin", "editor")
def update_policy(policy_id):
    claims = get_jwt()
    policy = ConsentPolicy.query.get_or_404(policy_id)
    if claims.get("role") != "admin" and policy.organization_id != claims["organization_id"]:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    for field in ["name", "description", "version", "is_active", "requires_explicit_consent", "retention_days"]:
        if field in data:
            setattr(policy, field, data[field])
    db.session.commit()
    return jsonify(policy.to_dict()), 200


@consents_bp.route("/policies/<policy_id>", methods=["DELETE"])
@jwt_required()
@require_role("admin")
def delete_policy(policy_id):
    policy = ConsentPolicy.query.get_or_404(policy_id)
    policy.is_active = False
    db.session.commit()
    return jsonify({"message": "Policy deactivated"}), 200


# ─── Records ─────────────────────────────────────────────────────────────────

@consents_bp.route("/records", methods=["POST"])
@jwt_required()
def create_record():
    """Record a data subject's consent decision."""
    data = request.get_json(silent=True) or {}
    required = ["policy_id", "data_subject_id", "status"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    valid_statuses = {"granted", "denied", "withdrawn", "pending"}
    if data["status"] not in valid_statuses:
        return jsonify({"error": f"status must be one of: {', '.join(valid_statuses)}"}), 400

    claims = get_jwt()
    policy = ConsentPolicy.query.get_or_404(data["policy_id"])
    if claims.get("role") != "admin" and policy.organization_id != claims["organization_id"]:
        return jsonify({"error": "Forbidden"}), 403

    expires_at = None
    if policy.retention_days:
        expires_at = _utcnow() + timedelta(days=policy.retention_days)

    record = ConsentRecord(
        organization_id=policy.organization_id,
        policy_id=data["policy_id"],
        user_id=get_jwt_identity(),
        data_subject_id=data["data_subject_id"],
        data_subject_email=data.get("data_subject_email"),
        status=data["status"],
        consent_method=data.get("consent_method", "api"),
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        metadata_=json.dumps(data.get("metadata", {})),
        granted_at=_utcnow() if data["status"] == "granted" else None,
        expires_at=expires_at,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@consents_bp.route("/records", methods=["GET"])
@jwt_required()
def list_records():
    """List consent records with optional filtering."""
    claims = get_jwt()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = ConsentRecord.query
    if claims.get("role") != "admin":
        query = query.filter_by(organization_id=claims["organization_id"])

    if request.args.get("policy_id"):
        query = query.filter_by(policy_id=request.args["policy_id"])
    if request.args.get("status"):
        query = query.filter_by(status=request.args["status"])
    if request.args.get("data_subject_id"):
        query = query.filter_by(data_subject_id=request.args["data_subject_id"])
    if request.args.get("data_subject_email"):
        query = query.filter(ConsentRecord.data_subject_email.ilike(f"%{request.args['data_subject_email']}%"))

    query = query.order_by(ConsentRecord.created_at.desc())
    return jsonify(paginate(query, page, per_page)), 200


@consents_bp.route("/records/<record_id>", methods=["GET"])
@jwt_required()
def get_record(record_id):
    claims = get_jwt()
    record = db.get_or_404(ConsentRecord, record_id)
    if claims.get("role") != "admin" and record.organization_id != claims["organization_id"]:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(record.to_dict()), 200


@consents_bp.route("/records/<record_id>/withdraw", methods=["PUT"])
@jwt_required()
def withdraw_consent(record_id):
    """Withdraw an existing consent record."""
    claims = get_jwt()
    record = db.get_or_404(ConsentRecord, record_id)
    if claims.get("role") != "admin" and record.organization_id != claims["organization_id"]:
        return jsonify({"error": "Forbidden"}), 403

    record.status = "withdrawn"
    record.withdrawn_at = _utcnow()
    db.session.commit()
    return jsonify(record.to_dict()), 200


@consents_bp.route("/records/export", methods=["GET"])
@jwt_required()
@require_role("admin", "editor")
def export_records():
    """Export consent records as CSV or JSON."""
    fmt = request.args.get("format", "csv").lower()
    claims = get_jwt()

    query = ConsentRecord.query
    if claims.get("role") != "admin":
        query = query.filter_by(organization_id=claims["organization_id"])

    records = query.order_by(ConsentRecord.created_at.desc()).all()
    timestamp = _utcnow().strftime("%Y%m%d_%H%M%S")

    if fmt == "json":
        output = BytesIO()
        output.write(json.dumps([r.to_dict() for r in records], indent=2).encode())
        output.seek(0)
        return send_file(output, mimetype="application/json", as_attachment=True,
                         download_name=f"consent_records_{timestamp}.json")

    # Default: CSV
    fieldnames = [
        "id", "organization_id", "policy_id", "data_subject_id", "data_subject_email",
        "status", "consent_method", "ip_address", "granted_at", "withdrawn_at",
        "expires_at", "created_at",
    ]
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in records:
        writer.writerow(r.to_dict())

    bytes_output = BytesIO(output.getvalue().encode())
    return send_file(bytes_output, mimetype="text/csv", as_attachment=True,
                     download_name=f"consent_records_{timestamp}.csv")
