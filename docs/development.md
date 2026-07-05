# Development Guide

This guide details the standard workflow for modifying and extending ConsentHub locally.

## Prerequisites

- **Python**: 3.12+
- **pip**: Latest version
- **Docker**: (Recommended for running full-stack tests)

---

## Backend Local Setup

1. **Initialize the Virtual Environment**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**

```bash
pip install -r requirements-dev.txt
```

3. **Configure Environment**

```bash
cp ../.env.example .env
```

4. **Launch the Development Server**

With `FLASK_ENV=development`, the server will automatically reload on code changes and use a local SQLite database by default.

```bash
export FLASK_ENV=development
export FLASK_APP=wsgi.py
python wsgi.py
```
*The API is now listening at `http://localhost:5000`.*

---

## Running the Test Suite

ConsentHub enforces strict test coverage using `pytest`.

```bash
# Run all tests
make test

# Run tests with HTML coverage report
make test-cov

# Execute a specific test file
pytest tests/test_consents.py -v
```

---

## Frontend Development

The ConsentHub dashboard is a vanilla HTML/JS/CSS application requiring zero build tools (no Webpack, no NPM installs).

1. Ensure the backend API is running locally.
2. Serve the `frontend/src` directory using any local web server, or simply open `frontend/src/index.html` in your browser.
3. API calls will default to `http://localhost:5000/api` unless overridden by `CONSENTHUB_API_URL`.

*Note: For the fastest evaluation, use the Mock API mode by ensuring `js/demo-mock-api.js` is loaded, which intercepts `fetch` calls and simulates the backend entirely within the browser.*

---

## Extending the API

To introduce a new API resource:

1. **Define the Route:** Create a new blueprint in `backend/app/api/<feature>.py`.
2. **Register the Blueprint:** Import and register it within `backend/app/__init__.py`.
3. **Define the Model:** Add the SQLAlchemy model to `backend/app/models/__init__.py`.
4. **Write Tests:** Author comprehensive tests in `backend/tests/test_<feature>.py`.

## Code Standards

- **Python**: Adhere to PEP8. Type hinting is strongly encouraged for all new function signatures.
- **JavaScript**: Write modern ES2020+ compatible code. Avoid introducing external framework dependencies.
