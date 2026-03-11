"""Users API blueprint."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app import db
from app.models import User
from app.utils import require_role, paginate, hash_password

users_bp = Blueprint("users", __name__)


@users_bp.route("", methods=["GET"])
@jwt_required()
def list_users():
    """List users. Admins see all; others see their org only."""
    claims = get_jwt()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = User.query
    if claims.get("role") != "admin":
        query = query.filter_by(organization_id=claims.get("organization_id"))

    query = query.order_by(User.created_at.desc())
    return jsonify(paginate(query, page, per_page)), 200


@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """Get a single user."""
    claims = get_jwt()
    user = db.get_or_404(User, user_id)

    # Only admins or the user themselves (or same org editor+) can view
    if (
        claims.get("role") != "admin"
        and get_jwt_identity() != user_id
        and claims.get("organization_id") != user.organization_id
    ):
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(user.to_dict()), 200


@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """Update a user."""
    claims = get_jwt()
    user = db.get_or_404(User, user_id)

    if claims.get("role") != "admin" and get_jwt_identity() != user_id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}

    if "name" in data:
        user.name = data["name"].strip()
    if "role" in data and claims.get("role") == "admin":
        user.role = data["role"]
    if "password" in data:
        user.password_hash = hash_password(data["password"])
    if "is_active" in data and claims.get("role") == "admin":
        user.is_active = data["is_active"]

    db.session.commit()
    return jsonify(user.to_dict()), 200


@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@require_role("admin")
def delete_user(user_id):
    """Deactivate a user."""
    user = db.get_or_404(User, user_id)
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "User deactivated"}), 200
