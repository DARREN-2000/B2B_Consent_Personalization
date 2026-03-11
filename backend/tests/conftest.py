"""Pytest configuration and shared fixtures."""

import pytest
from app import create_app, db as _db
from app.models import Organization, User
from app.utils import hash_password


@pytest.fixture(scope="session")
def app():
    """Create application instance for testing."""
    _app = create_app("testing")
    yield _app


@pytest.fixture(scope="session")
def db(app):
    """Create database tables once per test session."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(db, app):
    """Wrap each test in a transaction and roll back after."""
    with app.app_context():
        yield
        db.session.rollback()
        # Clean tables to ensure test isolation
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def org(app, db):
    """A sample organization."""
    with app.app_context():
        organization = Organization(
            name="Test Corp",
            domain="testcorp.example",
            industry="Technology",
            plan="pro",
        )
        db.session.add(organization)
        db.session.commit()
        db.session.refresh(organization)
        return organization.to_dict()


@pytest.fixture
def admin_user(app, db, org):
    """An admin user belonging to the sample org."""
    with app.app_context():
        user = User(
            organization_id=org["id"],
            email="admin@testcorp.example",
            name="Test Admin",
            password_hash=hash_password("TestPass123!"),
            role="admin",
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user.to_dict()


@pytest.fixture
def admin_token(client, admin_user):
    """JWT access token for the admin user."""
    resp = client.post("/api/auth/login", json={
        "email": "admin@testcorp.example",
        "password": "TestPass123!",
    })
    assert resp.status_code == 200, resp.json
    return resp.json["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """Authorization header dict for admin."""
    return {"Authorization": f"Bearer {admin_token}"}
