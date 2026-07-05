# Deployment Guide

ConsentHub supports both containerized deployment via Docker Compose and production-grade orchestration via Kubernetes Helm charts.

## Prerequisites

- **Docker:** Version 24+
- **Docker Compose:** v2+
- **Kubernetes:** kubectl configured, Helm 3.15+

---

## Single Node Deployment (Docker Compose)

Docker Compose is recommended for evaluation, small internal deployments, or development.

### Environment Configuration

Establish strong credentials before deploying:

```bash
cp .env.example .env
```
Edit `.env` and set cryptographically secure values for:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `ADMIN_API_KEY`
- `POSTGRES_PASSWORD`

### Launching the Stack

```bash
docker-compose up --build -d
```
This provisions:
- `db`: PostgreSQL 16 on an isolated internal network.
- `backend`: The Flask API listening on port 5000.
- `frontend`: The Nginx static server and dashboard on port 3000.

---

## Production Kubernetes Deployment (Helm)

The official Helm chart is the recommended method for enterprise production environments, providing built-in support for High Availability (HA) and autoscaling.

### 1. Repository Setup

ConsentHub leverages the Bitnami PostgreSQL subchart for robust database provisioning.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### 2. Installation

Install the chart into a dedicated namespace, providing your secrets dynamically.

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

### 3. Configuring Autoscaling (HPA)

To enable horizontal pod autoscaling for the API layer based on CPU/Memory utilization:

```bash
helm upgrade consenthub helm/consenthub \
  --reuse-values \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10
```

### 4. Verification

Confirm the status of the deployment:

```bash
kubectl get pods -n consenthub
kubectl get svc -n consenthub
kubectl get ingress -n consenthub
kubectl logs -n consenthub -l app.kubernetes.io/component=backend
```

---

## Essential Environment Variables

| Variable | Requirement | Purpose |
|----------|-------------|---------|
| `SECRET_KEY` | **Required** | Flask session cryptography seed. |
| `JWT_SECRET_KEY` | **Required** | Key for signing and verifying JWT tokens. |
| `ADMIN_API_KEY` | **Required** | Pre-shared key for initial admin bootstrapping. |
| `DATABASE_URL` | Optional | Explicit SQLAlchemy connection string (defaults to SQLite in development). |
| `CORS_ORIGINS` | Optional | Comma-separated list of permitted CORS origins. |
| `POSTGRES_PASSWORD` | Optional | Database password (required if using the bundled PostgreSQL container). |

## Probes and Observability

Both the API and Frontend containers expose standard health endpoints utilized by Docker `HEALTHCHECK` and Kubernetes liveness/readiness probes:
- Backend: `GET /api/health`
- Frontend: `GET /health` (Nginx native)
