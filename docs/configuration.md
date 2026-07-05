# Configuration

ConsentHub relies heavily on environment variables for twelve-factor app compatibility.

## Core Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Set to `development` to enable hot-reload and debug mode. |
| `SECRET_KEY` | - | **Required.** Cryptographic salt for Flask sessions. |
| `JWT_SECRET_KEY` | - | **Required.** Key used to sign JWTs. |
| `DATABASE_URL` | `sqlite:///...` | SQLAlchemy connection string (e.g., `postgresql://...`). |
| `CORS_ORIGINS` | `*` | Comma-separated list of allowed origins. |

## Advanced Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_ACCESS_TOKEN_EXPIRES` | `28800` | Access token lifespan in seconds (8 hours). |
| `JWT_REFRESH_TOKEN_EXPIRES` | `2592000` | Refresh token lifespan in seconds (30 days). |
| `DB_POOL_SIZE` | `5` | SQLAlchemy connection pool size. |
| `DB_MAX_OVERFLOW` | `10` | Maximum number of connections to allow beyond the pool size. |
