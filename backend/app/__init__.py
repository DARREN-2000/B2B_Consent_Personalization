"""ConsentHub Backend Application Factory"""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_name: str = "development"):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load config
    from app.config import config
    app.config.from_object(config[config_name])

    # Init extensions
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from app.api.health import health_bp
    from app.api.auth import auth_bp
    from app.api.consents import consents_bp
    from app.api.organizations import organizations_bp
    from app.api.users import users_bp
    from app.api.analytics import analytics_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(consents_bp, url_prefix="/api/consents")
    app.register_blueprint(organizations_bp, url_prefix="/api/organizations")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")

    # Create tables
    with app.app_context():
        db.create_all()

    return app
