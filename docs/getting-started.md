# Getting Started

ConsentHub is designed to be quick to evaluate and straightforward to deploy.

## Quick Start (Demo Mode)

The fastest way to experience ConsentHub is via our containerized Demo Mode, which uses SQLite and requires zero external database configuration.

```bash
git clone https://github.com/DARREN-2000/B2B_Consent_Personalization.git
cd B2B_Consent_Personalization

# Start the stack
make demo
```

Once running, navigate to `http://localhost:3000`. The API will be available at `http://localhost:5000/api`.

## Creating an Admin User

After starting the stack, create your first organizational admin user via the API:

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "name": "Admin User",
    "password": "SecurePass123!",
    "organization_id": "org-uuid-here",
    "role": "admin"
  }'
```

## Next Steps

- For local development and customization, see the [Development Guide](development.md).
- To configure for a production environment with PostgreSQL, see the [Configuration Guide](configuration.md) and [Installation Guide](installation.md).
