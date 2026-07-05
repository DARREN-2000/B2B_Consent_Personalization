# API Reference

Base URL: `http://localhost:5000/api` (development) / `https://your-domain.com/api` (production)

All protected endpoints require an authorization header:
```http
Authorization: Bearer <access_token>
```

---

## Health

### `GET /health`
Validates the availability of the API and its underlying datastore. No authentication required.

**Response 200**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:00:00",
  "version": "1.0.0",
  "database": "ok"
}
```

---

## Authentication

### `POST /auth/register`
Registers a new user and provisions access within a specific organization.

**Request Body**
```json
{
  "email": "user@company.com",
  "name": "Jane Doe",
  "password": "SecurePass123!",
  "organization_id": "uuid",
  "role": "editor"
}
```
*Valid Roles:* `admin` | `editor` | `viewer`

### `POST /auth/login`
Authenticates a user and issues JWT tokens.

**Request Body**
```json
{
  "email": "user@company.com",
  "password": "SecurePass123!"
}
```

**Response 200**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": { "id": "...", "role": "..." }
}
```

### `POST /auth/refresh`
Refreshes an expired access token using the refresh token (provided in the `Authorization` header).

### `GET /auth/me`
Retrieves the profile and context of the currently authenticated user.

---

## Consent Policies

### `POST /consents/policies`
Creates a new consent policy for the organization.
*Required Roles:* `admin`, `editor`

**Request Body**
```json
{
  "name": "Marketing Email Consent",
  "policy_type": "gdpr",
  "description": "Consent for marketing communications",
  "version": "1.0",
  "requires_explicit_consent": true,
  "retention_days": 730
}
```
*Valid Types:* `gdpr` | `ccpa` | `lgpd` | `custom`

### `GET /consents/policies`
Retrieves a paginated list of the organization's consent policies.
*Query Params:* `page`, `per_page`, `policy_type`, `is_active`

### `GET /consents/policies/<id>`
Retrieves details for a specific consent policy.

### `PUT /consents/policies/<id>`
Updates mutable fields of a consent policy.

### `DELETE /consents/policies/<id>`
Soft-deletes a policy (sets `is_active=false`).
*Required Roles:* `admin`

---

## Consent Records

### `POST /consents/records`
Records a data subject's explicit consent decision.

**Request Body**
```json
{
  "policy_id": "uuid",
  "data_subject_id": "user-12345",
  "data_subject_email": "end-user@example.com",
  "status": "granted",
  "consent_method": "web-form",
  "metadata": { "page": "/signup", "version": "2024-Q1" }
}
```
*Valid Status:* `granted` | `denied` | `withdrawn` | `pending`
*Valid Methods:* `web-form` | `api` | `email` | `paper`

### `GET /consents/records`
Retrieves a paginated list of consent records.
*Query Params:* `page`, `per_page`, `status`, `policy_id`, `data_subject_id`, `data_subject_email`

### `PUT /consents/records/<id>/withdraw`
Transitions a previously granted consent record to the `withdrawn` state, establishing an immutable audit timestamp.

### `GET /consents/records/export`
Exports all organizational consent records.
*Query Params:* `format=csv` (default) | `format=json`

---

## Analytics

### `GET /analytics/summary`
Returns aggregate operational statistics for the caller's organization.

**Response 200**
```json
{
  "total_records": 1240,
  "consent_rate_pct": 78.5,
  "by_status": { "granted": 974, "denied": 180, "withdrawn": 86 },
  "by_method": { "web-form": 900, "api": 340 },
  "by_policy": { "<policy_id>": 1240 }
}
```

### `GET /analytics/trends`
Returns a time-series breakdown of consent decisions.
*Query Params:* `days=30` (default)

---

## Organizations

*Required Roles:* `admin`
Endpoints for lifecycle management of tenants:
- `GET /organizations`
- `POST /organizations`
- `GET /organizations/<id>`
- `PUT /organizations/<id>`
- `DELETE /organizations/<id>`

---

## Standard Error Responses

ConsentHub standardizes errors using the following JSON envelope:

```json
{ "error": "Descriptive error message context" }
```

| HTTP Status | Context |
|-------------|---------|
| `400 Bad Request` | Missing required fields or malformed payload. |
| `401 Unauthorized` | Missing, invalid, or expired JWT. |
| `403 Forbidden` | Insufficient role authorization for action. |
| `404 Not Found` | Requested resource UUID does not exist or belong to the tenant. |
| `409 Conflict` | Unique constraint violation (e.g., email already exists). |
| `500 Internal Server Error` | Unhandled backend exception. |