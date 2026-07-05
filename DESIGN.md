# Design Decisions

This document captures the historical context and reasoning behind significant architectural and technological choices in ConsentHub.

## 1. Why Python / Flask?
**Context:** The API layer needed to be stateless, easy to read, and quick to extend.
**Decision:** Python 3.12 with Flask 3.
**Reasoning:** Flask provides the minimal necessary routing and request-handling primitives without the overhead of larger frameworks like Django. This keeps the codebase highly focused on the business logic of consent management. Python's ecosystem for data manipulation (which will be useful for future analytics features) is unmatched.

## 2. Why Vanilla HTML/JS for the Frontend?
**Context:** The administrative dashboard needed to be easy to deploy and maintain, avoiding the constant churn of the NPM ecosystem.
**Decision:** A zero-build-step SPA using vanilla HTML, CSS (with custom properties), and JavaScript.
**Reasoning:** By removing Node.js, Webpack, and framework dependencies (React, Vue) from the frontend, the barrier to entry for contributions is significantly lowered. It allows the frontend to be served efficiently by Nginx directly from an Alpine container, resulting in a tiny, ultra-fast image.

## 3. Why SQLAlchemy over Raw SQL?
**Context:** Need for a reliable, database-agnostic interface that supports migrations and complex queries (analytics).
**Decision:** SQLAlchemy 2.0.
**Reasoning:** While raw SQL can be faster for simple queries, SQLAlchemy provides a robust ORM that implicitly handles connection pooling, type coercion, and prevents SQL injection. Crucially, it allows developers to run the application against SQLite locally and PostgreSQL in production without changing code.

## 4. Why Soft Deletes for Policies?
**Context:** Consent policies represent a legal contract at a point in time.
**Decision:** Policies are never `DELETE`d from the database; they are marked `is_active=False`.
**Reasoning:** If a policy were deleted, the historical consent records tied to that policy would become orphaned and lose their context, violating the core principle of absolute auditability.

## 5. Why JWTs instead of Stateful Sessions?
**Context:** The application needs to scale horizontally in Kubernetes.
**Decision:** Short-lived JWTs (Access) + Long-lived JWTs (Refresh).
**Reasoning:** Stateless tokens mean the API does not need to query a session store (like Redis or the DB) on every request to verify authorization. This reduces database load and simplifies scaling. The tradeoff is the inability to immediately revoke an access token, mitigated by keeping their lifespan short (8 hours).