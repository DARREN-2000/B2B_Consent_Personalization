# Welcome to ConsentHub

> **ConsentHub** is a production-ready, industry-standard B2B SaaS platform for managing data-subject consent across GDPR, CCPA, LGPD and custom privacy frameworks.

It enables businesses to create consent policies, record granular consent decisions, and gain full audit visibility — all via a REST API and an intuitive admin dashboard.

## Overview

ConsentHub provides a robust architecture for consent management, ensuring that every user decision is reliably recorded, auditable, and isolated securely within multi-tenant organizations.

### Key Capabilities

- **Consent Policies**: Create GDPR, CCPA, LGPD, or custom policies with version control.
- **Granular Consent Records**: Record grant, deny, and withdraw decisions with a full immutable audit trail.
- **Multi-tenant Data Isolation**: Strict organizational scoping for B2B deployments.
- **Robust Authentication**: JWT-based authentication with Role-Based Access Control (Admin, Editor, Viewer).
- **High-Performance Architecture**: Stateless Python API backed by PostgreSQL, scaling horizontally via Kubernetes HPA.

## Quick Links

- [Getting Started](getting-started.md)
- [Architecture Overview](architecture.md)
- [API Reference](api.md)
- [Deployment Guide](deployment.md)

---

## Why ConsentHub?

Managing consent in an increasingly regulated environment is complex. Traditional platforms are either too heavyweight or lack developer-friendly primitives. ConsentHub strikes the balance: a highly performant API, coupled with a seamless dashboard, ready to run in any Kubernetes environment or simple Docker compose stack.
