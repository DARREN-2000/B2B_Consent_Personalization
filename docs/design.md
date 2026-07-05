# Design Philosophy

ConsentHub is engineered around three core principles: **Auditability**, **Multi-tenant Isolation**, and **Operational Simplicity**.

## 1. Absolute Auditability
Consent is fundamentally about proving compliance. Therefore, the state of a consent record is not merely updated; state transitions are appended or marked immutably.
- **Context Preservation:** Every consent decision captures the timestamp, the method (e.g., `web-form`, `api`), and contextual metadata.
- **Withdrawals:** Withdrawing consent does not delete the record. It transitions the `status` to `withdrawn` and records a `withdrawn_at` timestamp, providing a complete historical ledger.

## 2. Multi-tenant Isolation by Default
As a B2B platform, ensuring tenant data remains strictly segregated is paramount.
- **Implicit Scoping:** Every authenticated request is bound to an `organization_id` extracted securely from the JWT.
- **ORM Guards:** The SQLAlchemy models and repository layers mandate `organization_id` filters on all queries, making accidental cross-tenant data leakage structurally impossible.

## 3. Operational Simplicity
Enterprise software often suffers from excessive complexity. ConsentHub deliberately minimizes its operational footprint.
- **Zero-Build Frontend:** The dashboard is built with vanilla HTML, CSS, and Javascript. There is no Node.js compilation step, no Webpack configuration, and no NPM dependency hell. It can be served by any static file server.
- **Stateless API:** The Flask backend relies entirely on the database for state, making it trivially easy to scale horizontally behind a load balancer.
