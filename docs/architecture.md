# Architecture Overview

ConsentHub employs a robust, scalable multi-tier architecture suitable for enterprise B2B SaaS deployments.

## System Diagram

The system operates across three primary layers: the Edge/Frontend, the Application API, and the Persistence Layer.

```mermaid
graph TD
    User([User / Browser])
    Ingress[Nginx / Ingress Controller\nTLS termination, routing]
    API[Backend Flask API\nPython 3.12]
    SPA[Frontend Nginx SPA\nHTML/JS/CSS]
    DB[(PostgreSQL 16\nor SQLite)]

    User -->|HTTPS| Ingress
    Ingress -->|/api/*| API
    Ingress -->|/*| SPA
    API -->|SQLAlchemy ORM| DB

    classDef default fill:#fff,stroke:#333,stroke-width:2px;
    classDef highlight fill:#f9f9f9,stroke:#000,stroke-width:2px;
    class User,DB highlight;
```

## Data Models

The data model strictly enforces multi-tenant isolation through an Organization-scoped hierarchy.

```mermaid
erDiagram
    ORGANIZATION ||--o{ USER : contains
    ORGANIZATION ||--o{ CONSENT_POLICY : owns
    ORGANIZATION ||--o{ CONSENT_RECORD : records
    CONSENT_POLICY ||--o{ CONSENT_RECORD : defines
    USER ||--o{ CONSENT_RECORD : records_audit

    ORGANIZATION {
        uuid id PK
        string name
    }
    USER {
        uuid id PK
        uuid organization_id FK
        string email
        string role
        string password_hash
    }
    CONSENT_POLICY {
        uuid id PK
        uuid organization_id FK
        string name
        string policy_type
        string version
    }
    CONSENT_RECORD {
        uuid id PK
        uuid organization_id FK
        uuid policy_id FK
        string data_subject_id
        string status
        string consent_method
    }
```

## Request Lifecycle

1. **Authentication:** The `POST /api/auth/login` endpoint validates credentials using bcrypt and issues JWT access and refresh tokens.
2. **Authorization & JWT Validation:** Protected endpoints require a valid `Authorization: Bearer <token>` header. `Flask-JWT-Extended` decodes the token, exposing claims like `user_id`, `role`, and `organization_id`.
3. **Role-Based Guard:** The `require_role()` decorator intercepts the request, ensuring the user possesses the necessary privileges (`admin`, `editor`, or `viewer`).
4. **Tenant Isolation:** SQLAlchemy queries are implicitly or explicitly scoped to the user's `organization_id`, ensuring absolute data segregation between tenants.
5. **Execution & Audit:** State-modifying requests create or update records. Consent records immutably capture context (method, timestamp) to fulfill compliance audit requirements.

## Scalability and Performance

- **Stateless Application Layer:** The Flask API maintains zero local state between requests, allowing horizontal scaling using Kubernetes Horizontal Pod Autoscaler (HPA).
- **Database Pooling:** SQLAlchemy manages connection pooling to optimize PostgreSQL throughput.
- **Production Edge:** Nginx handles TLS termination and serves the static Single Page Application (SPA), completely decoupling the UI load from the API layer.
