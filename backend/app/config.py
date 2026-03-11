"""Application configuration."""

import os
from datetime import timedelta


class BaseConfig:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-change-me-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get("JWT_ACCESS_HOURS", "8")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", "30")))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "changeme-admin-key")
    PAGE_SIZE = int(os.environ.get("PAGE_SIZE", "20"))


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///consenthub_dev.db"
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///consenthub.db")
    # Enforce strong secret in prod
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "https://yourdomain.com")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
