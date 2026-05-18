# ConsentHub — B2B Consent Management & Personalization Platform

> **ConsentHub** is a production-ready, industry-standard B2B SaaS platform for managing data-subject consent across GDPR, CCPA, LGPD and custom privacy frameworks. It enables businesses to create consent policies, record granular consent decisions, and gain full audit visibility — all via a REST API and an intuitive admin dashboard.

---

## 🏗️ Project Structure

```
consenthub/
├── backend/                  # Python/Flask REST API
│   ├── app/
│   │   ├── __init__.py       # Application factory
│   │   ├── config.py         # Environment configurations
│   │   ├── api/              # Blueprints (routes)
│   │   │   ├── health.py
│   │   │   ├── auth.py
│   │   │   ├── consents.py
│   │   │   ├── organizations.py
│   │   │   ├── users.py
│   │   │   └── analytics.py
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   └── __init__.py
│   │   └── utils/            # Auth helpers, pagination
│   │       └── __init__.py
│   ├── tests/                # pytest test suite (24+ tests)
│   ├── wsgi.py               # WSGI entry point
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   └── Dockerfile            # Multi-stage production image
│
├── frontend/                 # Static admin dashboard (HTML/CSS/JS)
│   ├── src/
│   │   ├── index.html        # Single-page dashboard
│   │   ├── css/styles.css
│   │   └── js/
│   │       ├── api.js        # Centralized API client
│   │       └── dashboard.js  # Dashboard logic
│   ├── nginx.conf
│   └── Dockerfile            # Nginx static server
│
├── helm/consenthub/          # Kubernetes Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── secret.yaml
│       ├── hpa.yaml
│       ├── serviceaccount.yaml
│       └── _helpers.tpl
│
├── docs/                     # Documentation
│   ├── API.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPMENT.md
│   └── ARCHITECTURE.md
│
├── .github/workflows/        # GitHub Actions CI/CD
│   ├── ci.yml                # Test + Docker build + Helm lint
│   └── cd.yml                # Build, push images, Helm deploy
│
├── docker-compose.yml        # Production stack
├── docker-compose.dev.yml    # Development overrides
├── .env.example              # Environment variable template
├── Makefile                  # Developer convenience targets
└── README.md
```

---

## ✨ Key Features

| Feature | Details |
|---|---|
| **Consent Policies** | Create GDPR, CCPA, LGPD, or custom policies with version control |
| **Consent Records** | Record grant/deny/withdraw decisions with full audit trail |
| **JWT Auth** | Access + refresh tokens, role-based access (admin / editor / viewer) |
| **Multi-tenancy** | Organization-scoped data isolation |
| **Analytics** | Consent rate, daily trends, method breakdown |
| **Export** | CSV & JSON export of all consent records |
| **Admin Dashboard** | Full SPA with charts, tables, modals, and filters |
| **Docker** | Multi-stage builds for backend + Nginx frontend |
| **Helm Chart** | Production-ready Kubernetes deployment with HPA & Ingress |
| **CI/CD** | GitHub Actions: test → build → push → deploy |

---

## 🚀 Quick Start (Docker Compose)

### 0. Fast demo mode (free & easiest)

```bash
make demo
```

This starts backend + frontend with SQLite (no PostgreSQL setup), so you can run a working demo immediately.

### 1. Clone & configure

```bash
git clone https://github.com/DARREN-2000/B2B_Consent_Personalization.git
cd B2B_Consent_Personalization
cp .env.example .env
# Edit .env with your secrets
```

### 2. Start the stack

```bash
make up
# or: docker-compose up --build -d
```

### 3. Open the dashboard

```
http://localhost:3000
```

### 4. Create your first admin user

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "name": "Admin User",
    "password": "SecurePass123!",
    "organization_id": "<your-org-id>",
    "role": "admin"
  }'
```

---

## 🛠️ Local Development

```bash
# Setup Python virtualenv
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Run tests
make test
# or: pytest

# Start backend with hot-reload
FLASK_ENV=development python wsgi.py
```

---

## 🐳 Docker

```bash
# Build images individually
docker build -t consenthub/backend:latest ./backend
docker build -t consenthub/frontend:latest ./frontend

# Run full stack
docker-compose up -d

# View logs
docker-compose logs -f backend
```

---

## ☸️ Kubernetes / Helm

```bash
# Lint
helm lint helm/consenthub

# Install
helm upgrade --install consenthub helm/consenthub \
  --namespace consenthub --create-namespace \
  --set backend.secrets.secretKey="your-secret" \
  --set backend.secrets.jwtSecretKey="your-jwt-secret" \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=consenthub.yourdomain.com

# Uninstall
helm uninstall consenthub -n consenthub
```

---

## 🔌 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/health` | Health check |
| `POST` | `/api/auth/login` | Get JWT tokens |
| `POST` | `/api/auth/register` | Register user |
| `GET`  | `/api/auth/me` | Current user |
| `POST` | `/api/consents/policies` | Create policy |
| `GET`  | `/api/consents/policies` | List policies |
| `POST` | `/api/consents/records` | Record consent |
| `GET`  | `/api/consents/records` | List records |
| `PUT`  | `/api/consents/records/<id>/withdraw` | Withdraw consent |
| `GET`  | `/api/consents/records/export` | Export CSV/JSON |
| `GET`  | `/api/analytics/summary` | Consent stats |
| `GET`  | `/api/analytics/trends` | Daily trends |

See [`docs/API.md`](docs/API.md) for full documentation.

---

## 🧪 Tests

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

24 tests covering: health, auth, consent policies, consent records, analytics.

---

## 🔒 Security

- Passwords hashed with **bcrypt**
- **JWT** with configurable expiry (access + refresh)
- Role-based access control (RBAC)
- Organization-scoped data isolation
- Non-root Docker user
- Kubernetes secrets + `readOnlyRootFilesystem` security context

---

## 📄 License

[MIT](LICENSE)
