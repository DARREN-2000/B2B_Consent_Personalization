"""Organizations API blueprint."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app import db
from app.models import Organization
from app.utils import require_role, paginate

organizations_bp = Blueprint("organizations", __name__)


@organizations_bp.route("", methods=["GET"])
@jwt_required()
@require_role("admin")
def list_organizations():
    """List all organizations (admin only)."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = Organization.query.order_by(Organization.created_at.desc())
    return jsonify(paginate(query, page, per_page)), 200


@organizations_bp.route("", methods=["POST"])
@jwt_required()
@require_role("admin")
def create_organization():
    """Create a new organization."""
    data = request.get_json(silent=True) or {}
    required = ["name", "domain"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if Organization.query.filter_by(domain=data["domain"].lower()).first():
        return jsonify({"error": "Domain already registered"}), 409

    org = Organization(
        name=data["name"].strip(),
        domain=data["domain"].lower().strip(),
        industry=data.get("industry"),
        plan=data.get("plan", "free"),
    )
    db.session.add(org)
    db.session.commit()
    return jsonify(org.to_dict()), 201


@organizations_bp.route("/<org_id>", methods=["GET"])
@jwt_required()
def get_organization(org_id):
    """Get a single organization. Users can only view their own org."""
    claims = get_jwt()
    if claims.get("role") != "admin" and claims.get("organization_id") != org_id:
        return jsonify({"error": "Forbidden"}), 403

    org = Organization.query.get_or_404(org_id)
    return jsonify(org.to_dict()), 200


@organizations_bp.route("/<org_id>", methods=["PUT"])
@jwt_required()
@require_role("admin", "editor")
def update_organization(org_id):
    """Update an organization."""
    claims = get_jwt()
    if claims.get("role") != "admin" and claims.get("organization_id") != org_id:
        return jsonify({"error": "Forbidden"}), 403

    org = Organization.query.get_or_404(org_id)
    data = request.get_json(silent=True) or {}

    for field in ["name", "industry", "plan"]:
        if field in data:
            setattr(org, field, data[field])

    db.session.commit()
    return jsonify(org.to_dict()), 200


@organizations_bp.route("/<org_id>", methods=["DELETE"])
@jwt_required()
@require_role("admin")
def delete_organization(org_id):
    """Soft-delete an organization by deactivating it."""
    org = Organization.query.get_or_404(org_id)
    org.is_active = False
    db.session.commit()
    return jsonify({"message": "Organization deactivated"}), 200
