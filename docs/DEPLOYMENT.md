# Deployment Guide

## Prerequisites

- Docker 24+
- Docker Compose v2
- (Kubernetes) kubectl + Helm 3.15+

---

## Docker Compose (recommended for small deployments)

### Free/easy demo deployment

```bash
docker-compose -f docker-compose.demo.yml up --build -d
```

This mode runs:
- `backend`  — Flask API using local SQLite (`/app/data/consenthub_demo.db`)
- `frontend` — Nginx dashboard on port 3000

No PostgreSQL provisioning is required, making it ideal for demos.
For safety, this mode defaults CORS to `http://localhost:3000` and uses demo secrets unless you override them in your environment.
SQLite demo data is persisted in the `demo_data` Docker volume.
⚠️ Demo secrets are intentionally weak defaults and must be overridden before any internet-facing deployment.

### Production

```bash
cp .env.example .env
# Set strong SECRET_KEY, JWT_SECRET_KEY, ADMIN_API_KEY, POSTGRES_PASSWORD

docker-compose up --build -d
```

Services:
- `db`       — PostgreSQL 16 on internal network
- `backend`  — Flask API on port 5000
- `frontend` — Nginx dashboard on port 3000

### Development (hot-reload)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## Kubernetes via Helm

### 1. Add Bitnami repo (for PostgreSQL subchart)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### 2. Install

```bash
helm upgrade --install consenthub helm/consenthub \
  --namespace consenthub \
  --create-namespace \
  --set image.backend.repository=ghcr.io/yourorg/consenthub-backend \
  --set image.backend.tag=1.0.0 \
  --set image.frontend.repository=ghcr.io/yourorg/consenthub-frontend \
  --set image.frontend.tag=1.0.0 \
  --set backend.secrets.secretKey="$(openssl rand -hex 32)" \
  --set backend.secrets.jwtSecretKey="$(openssl rand -hex 32)" \
  --set backend.secrets.adminApiKey="$(openssl rand -hex 16)" \
  --set postgresql.auth.password="$(openssl rand -hex 16)" \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=consenthub.yourdomain.com
```

### 3. Enable autoscaling

```bash
helm upgrade consenthub helm/consenthub \
  --reuse-values \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10
```

### 4. Verify

```bash
kubectl get pods -n consenthub
kubectl get svc -n consenthub
kubectl logs -n consenthub -l app.kubernetes.io/component=backend
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session secret |
| `JWT_SECRET_KEY` | Yes | JWT signing key |
| `ADMIN_API_KEY` | Yes | Admin API key for sensitive ops |
| `DATABASE_URL` | No | Full DB URL (defaults to SQLite in dev) |
| `FLASK_ENV` | No | `development` / `production` |
| `CORS_ORIGINS` | No | Allowed CORS origins (comma-separated) |
| `PORT` | No | API listen port (default 5000) |
| `POSTGRES_DB` | No | PostgreSQL database name |
| `POSTGRES_USER` | No | PostgreSQL username |
| `POSTGRES_PASSWORD` | No | PostgreSQL password |

---

## Health Checks

- Backend: `GET /api/health`
- Frontend: `GET /health` (nginx)

Both are configured as Docker `HEALTHCHECK` and Kubernetes liveness/readiness probes.
