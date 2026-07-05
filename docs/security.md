# Security Posture

ConsentHub is designed to securely manage sensitive PII (Personally Identifiable Information) and compliance data.

## Authentication & Authorization

- **Password Storage:** User passwords are theoretically irreversible, hashed using `bcrypt` with a work factor (cost) of 12.
- **Session Management:** Stateless JSON Web Tokens (JWT) via `Flask-JWT-Extended`.
    - **Access Tokens:** Short-lived (default 8 hours).
    - **Refresh Tokens:** Long-lived (default 30 days) used to rotate access tokens without re-prompting credentials.
- **Role-Based Access Control (RBAC):** Hierarchical roles (`admin`, `editor`, `viewer`) are enforced at the API route level using a custom `@require_role` decorator.

## Data Protection

- **Transit:** The provided Helm charts configure Kubernetes Ingress for TLS termination, ensuring all data in transit is encrypted via HTTPS.
- **At Rest:** Database encryption at rest relies on the underlying PostgreSQL infrastructure provisioning (e.g., AWS RDS KMS, GCP Cloud SQL).
- **Tenant Isolation:** Mandatory `organization_id` filters on all database queries prevent cross-tenant access.

## Container Security

- **Non-Root Execution:** Docker containers are configured to run as non-root users where applicable.
- **Read-Only Filesystems:** Helm charts support deploying the backend with a `readOnlyRootFilesystem` security context, preventing malicious runtime tampering.
- **Secret Management:** All sensitive configuration (keys, database passwords) is passed exclusively via environment variables or Kubernetes Secrets, never hardcoded.