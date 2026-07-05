# Roadmap

This document outlines the high-level roadmap for ConsentHub. This is a living document and priorities may shift based on community feedback.

## Current Status (v1.0.0)
*   [x] Core API (Policies, Records)
*   [x] Multi-tenant isolation (Organizations)
*   [x] JWT Authentication & RBAC
*   [x] Docker Compose deployment
*   [x] Kubernetes Helm Chart
*   [x] Static SPA Dashboard
*   [x] Analytics & Exports

## Near-Term (Next 3-6 Months)
*   **Webhooks:** Outbound webhooks to notify external systems when consent state changes (e.g., sync to a CRM).
*   **SSO Integration:** SAML/OIDC support for logging into the admin dashboard via Okta/Azure AD.
*   **Enhanced API Keys:** Finer-grained API keys scoped to specific policies for external ingestion.
*   **Frontend Testing:** Add comprehensive e2e tests for the dashboard using Playwright or Cypress.

## Medium-Term (6-12 Months)
*   **Audit Log Streaming:** Native support for streaming the immutable audit log directly to Kafka or AWS Kinesis.
*   **Data Subject Portal:** A customizable, embeddable widget or hosted page where end-users can manage their own consent preferences directly.
*   **Advanced Analytics:** Deeper filtering and time-series analysis in the dashboard.

## Long-Term (12+ Months)
*   **Multi-Region Data Residency:** Support for routing and storing consent records in specific geographic regions to comply with strict localization laws.
*   **Machine Learning Insights:** Anomaly detection for consent withdrawal rates.