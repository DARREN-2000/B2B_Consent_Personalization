# Frequently Asked Questions

### Can ConsentHub manage both GDPR and CCPA compliance?
Yes. ConsentHub utilizes a flexible `policy_type` field. You can create distinct policies for GDPR, CCPA, LGPD, or any custom regional framework, and track user consent against each policy independently.

### Does ConsentHub support Single Sign-On (SSO)?
Currently, ConsentHub supports internal JWT-based authentication via email and password. SAML and OIDC support for enterprise SSO is planned for a future release (see [Roadmap](../ROADMAP.md)).

### Can I run ConsentHub without PostgreSQL?
Yes, for development and demonstration purposes, ConsentHub defaults to a local SQLite database if `DATABASE_URL` is not provided. However, SQLite is **not** supported or recommended for production deployments.

### How do I embed ConsentHub into my existing application?
ConsentHub is an API-first platform. Your existing web application, mobile app, or backend services can communicate directly with the `/api/consents/records` endpoints using an API key or User JWT to record consent events natively. The provided frontend is strictly an administrative dashboard.

### Is the data encrypted?
Data in transit should be encrypted by configuring TLS on your Ingress controller or Load Balancer. Data at rest encryption should be handled by your database infrastructure provider (e.g., AWS RDS KMS encryption).