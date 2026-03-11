"""Database models for ConsentHub."""

from app import db
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Organization(db.Model):
    """Represents a B2B customer organization."""
    __tablename__ = "organizations"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    industry = db.Column(db.String(100))
    plan = db.Column(db.String(50), default="free")  # free, starter, pro, enterprise
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    users = db.relationship("User", backref="organization", lazy=True, cascade="all, delete-orphan")
    consent_policies = db.relationship("ConsentPolicy", backref="organization", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "industry": self.industry,
            "plan": self.plan,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class User(db.Model):
    """Represents an admin or end-user within an organization."""
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey("organizations.id"), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="viewer")  # admin, editor, viewer
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    consent_records = db.relationship("ConsentRecord", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
        }


class ConsentPolicy(db.Model):
    """Defines a consent policy for an organization (e.g. GDPR, CCPA)."""
    __tablename__ = "consent_policies"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey("organizations.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    policy_type = db.Column(db.String(50), nullable=False)  # gdpr, ccpa, lgpd, custom
    version = db.Column(db.String(20), default="1.0")
    is_active = db.Column(db.Boolean, default=True)
    requires_explicit_consent = db.Column(db.Boolean, default=True)
    retention_days = db.Column(db.Integer, default=365)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    consent_records = db.relationship("ConsentRecord", backref="policy", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "name": self.name,
            "description": self.description,
            "policy_type": self.policy_type,
            "version": self.version,
            "is_active": self.is_active,
            "requires_explicit_consent": self.requires_explicit_consent,
            "retention_days": self.retention_days,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ConsentRecord(db.Model):
    """Records an individual's consent decision against a policy."""
    __tablename__ = "consent_records"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey("organizations.id"), nullable=False)
    policy_id = db.Column(db.String(36), db.ForeignKey("consent_policies.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    data_subject_id = db.Column(db.String(255), nullable=False)  # external ID or email of end-user
    data_subject_email = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="pending")  # granted, denied, withdrawn, pending
    consent_method = db.Column(db.String(50))  # web-form, api, email, paper
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    metadata_ = db.Column("metadata", db.Text)  # JSON blob for extra attributes
    granted_at = db.Column(db.DateTime)
    withdrawn_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "policy_id": self.policy_id,
            "user_id": self.user_id,
            "data_subject_id": self.data_subject_id,
            "data_subject_email": self.data_subject_email,
            "status": self.status,
            "consent_method": self.consent_method,
            "ip_address": self.ip_address,
            "metadata": json.loads(self.metadata_) if self.metadata_ else {},
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "withdrawn_at": self.withdrawn_at.isoformat() if self.withdrawn_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
