# Architecture Overview

## System Diagram

```
                    ┌──────────────────────────────┐
                    │       User (Browser)         │
                    └──────────┬───────────────────┘
                               │ HTTPS
                    ┌──────────▼───────────────────┐
                    │   Nginx / Ingress Controller  │
                    │   (TLS termination, routing)  │
                    └────┬─────────────────────┬────┘
                         │ /api/*              │ /*
           ┌─────────────▼──────────┐  ┌──────▼────────────────┐
           │   Backend (Flask API)  │  │  Frontend (Nginx SPA) │
           │   Python 3.12          │  │  HTML + CSS + JS      │
           │   Flask-SQLAlchemy     │  │  Chart.js             │
           │   Flask-JWT-Extended   │  └───────────────────────┘
           │   bcrypt               │
           └─────────────┬──────────┘
                         │ SQLAlchemy ORM
           ┌─────────────▼──────────┐
           │   PostgreSQL 16        │
           │   (or SQLite for dev)  │
           └────────────────────────┘
```

---

## Data Models

```
Organization
  └── has many Users
  └── has many ConsentPolicies
        └── has many ConsentRecords
  └── has many ConsentRecords (directly)

User ──────── belongs to Organization
ConsentPolicy ── belongs to Organization
ConsentRecord ── belongs to Organization
             ── belongs to ConsentPolicy
             ── belongs to User (who recorded it)
```

---

## Request Flow

1. **Login** — `POST /api/auth/login` → returns JWT access + refresh tokens
2. **Authenticated calls** — include `Authorization: Bearer <token>` header
3. **JWT verification** — `Flask-JWT-Extended` validates and extracts claims (user_id, role, organization_id)
4. **Role guard** — `require_role()` decorator checks if user's role is in allowed set
5. **Org isolation** — non-admin users see only their own organization's data
6. **DB query** — SQLAlchemy ORM query with filters → returns JSON
7. **Audit** — every consent record captures IP, user-agent, method, and timestamp

---

## Auth & Security

- Passwords: **bcrypt** (cost 12)
- JWT: HS256, short-lived access token (8h default) + long-lived refresh token (30d)
- Additional JWT claims: `role`, `organization_id`, `name`
- RBAC: `admin` > `editor` > `viewer`
- All secrets in environment variables / Kubernetes Secrets

---

## Scalability Notes

- Stateless backend → horizontal scaling via Kubernetes HPA
- Database connection pooling via SQLAlchemy
- For high-throughput, swap SQLite → PostgreSQL (already supported via `DATABASE_URL`)
- For async event-driven consent webhooks, add Celery + Redis (future roadmap)

---

## Technology Choices

| Layer | Technology | Reason |
|-------|-----------|--------|
| API | Flask 3 | Lightweight, battle-tested, easy to extend |
| ORM | SQLAlchemy 2 | Full-featured, supports multiple databases |
| Auth | Flask-JWT-Extended | Standard JWT with refresh token support |
| Frontend | Vanilla JS + Chart.js | Zero build toolchain, instant start |
| Container | Docker + Nginx | Industry standard |
| Orchestration | Helm + Kubernetes | Cloud-native, production-ready |
| CI/CD | GitHub Actions | Free, tight GitHub integration |
