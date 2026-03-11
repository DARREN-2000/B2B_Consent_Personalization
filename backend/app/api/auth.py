"""Authentication API blueprint."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from datetime import datetime, timezone

from app import db
from app.models import User
from app.utils import hash_password, check_password


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user (admin only in production via invite flow)."""
    data = request.get_json(silent=True) or {}

    required = ["email", "name", "password", "organization_id"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        organization_id=data["organization_id"],
        email=data["email"].lower().strip(),
        name=data["name"].strip(),
        password_hash=hash_password(data["password"]),
        role=data.get("role", "viewer"),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Obtain JWT access + refresh tokens."""
    data = request.get_json(silent=True) or {}

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"].lower().strip()).first()
    if not user or not check_password(data["password"], user.password_hash):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403

    user.last_login = _utcnow()
    db.session.commit()

    additional_claims = {
        "role": user.role,
        "organization_id": user.organization_id,
        "name": user.name,
    }
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Issue a new access token using a valid refresh token."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        return jsonify({"error": "User not found or inactive"}), 404

    additional_claims = {
        "role": user.role,
        "organization_id": user.organization_id,
        "name": user.name,
    }
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Return current authenticated user profile."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200
