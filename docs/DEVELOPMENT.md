# Development Guide

## Prerequisites

- Python 3.12+
- pip
- Docker (optional but recommended)
- Node.js (optional — frontend is pure HTML/JS, no build step)

---

## Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Copy and edit environment file
cp ../.env.example .env
```

### Running locally

```bash
export FLASK_ENV=development
export FLASK_APP=wsgi.py
python wsgi.py
# API available at http://localhost:5000
```

### Running tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific file
pytest tests/test_consents.py -v
```

---

## Project Layout (Backend)

```
backend/app/
├── __init__.py       Application factory (create_app)
├── config.py         Config classes: Dev / Test / Prod
├── api/
│   ├── health.py     GET /api/health
│   ├── auth.py       POST /api/auth/login|register|refresh, GET /me
│   ├── consents.py   CRUD policies + records + export
│   ├── organizations.py  CRUD organizations
│   ├── users.py      CRUD users
│   └── analytics.py  Summary, trends, overview
├── models/
│   └── __init__.py   Organization, User, ConsentPolicy, ConsentRecord
└── utils/
    └── __init__.py   hash_password, check_password, require_role, paginate
```

---

## Adding a New API Endpoint

1. Create or edit a blueprint in `backend/app/api/`
2. Register it in `backend/app/__init__.py` via `app.register_blueprint()`
3. Add model(s) in `backend/app/models/__init__.py`
4. Write tests in `backend/tests/test_<feature>.py`

---

## Frontend

The frontend is a zero-build-step SPA:

```
frontend/src/
├── index.html     Single HTML file — all pages rendered dynamically
├── css/styles.css Design system (CSS variables, components)
└── js/
    ├── api.js       Thin wrapper around fetch() for all API calls
    └── dashboard.js All page logic, event handlers, charts
```

To work on the frontend, simply open `frontend/src/index.html` in a browser (point `CONSENTHUB_API_URL` to your running backend).

---

## Code Style

- Python: PEP8, type hints encouraged
- JavaScript: ES2020+, no framework
- No linting config is enforced in CI currently — contributions welcome
