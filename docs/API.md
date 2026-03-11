# ConsentHub API Reference

Base URL: `http://localhost:5000/api` (development)

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## Health

### `GET /health`

No authentication required.

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

Register a new user.

**Body**
```json
{
  "email": "user@company.com",
  "name": "Jane Doe",
  "password": "SecurePass123!",
  "organization_id": "uuid",
  "role": "editor"
}
```

**Roles:** `admin` | `editor` | `viewer`

---

### `POST /auth/login`

**Body**
```json
{ "email": "user@company.com", "password": "SecurePass123!" }
```

**Response 200**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": { ... }
}
```

---

### `POST /auth/refresh`

Use the refresh token (in `Authorization` header) to get a new access token.

---

### `GET /auth/me`

Returns the currently authenticated user's profile.

---

## Consent Policies

### `POST /consents/policies`

**Roles:** admin, editor

**Body**
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

`policy_type`: `gdpr` | `ccpa` | `lgpd` | `custom`

---

### `GET /consents/policies`

Query params: `page`, `per_page`, `policy_type`, `is_active`

---

### `GET /consents/policies/<id>`

---

### `PUT /consents/policies/<id>`

---

### `DELETE /consents/policies/<id>`

Soft-deletes (sets `is_active=false`). **Roles:** admin only.

---

## Consent Records

### `POST /consents/records`

Record a data subject's consent decision.

**Body**
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

`status`: `granted` | `denied` | `withdrawn` | `pending`
`consent_method`: `web-form` | `api` | `email` | `paper`

---

### `GET /consents/records`

Query params: `page`, `per_page`, `status`, `policy_id`, `data_subject_id`, `data_subject_email`

---

### `GET /consents/records/<id>`

---

### `PUT /consents/records/<id>/withdraw`

Sets status to `withdrawn` and records `withdrawn_at` timestamp.

---

### `GET /consents/records/export`

Query params: `format=csv` (default) | `format=json`

Returns a file download.

---

## Analytics

### `GET /analytics/summary`

Returns aggregate consent statistics for the caller's organization.

```json
{
  "total_records": 1240,
  "consent_rate_pct": 78.5,
  "by_status": { "granted": 974, "denied": 180, "withdrawn": 86 },
  "by_method": { "web-form": 900, "api": 340 },
  "by_policy": { "<policy_id>": 1240 }
}
```

---

### `GET /analytics/trends?days=30`

Returns daily grant/denial breakdown.

---

### `GET /analytics/overview`

**Roles:** admin only. Platform-wide stats.

---

## Organizations

### `GET /organizations` — admin only
### `POST /organizations` — admin only
### `GET /organizations/<id>`
### `PUT /organizations/<id>`
### `DELETE /organizations/<id>` — soft delete, admin only

---

## Error Responses

All errors return JSON:

```json
{ "error": "Description of error" }
```

| Code | Meaning |
|------|---------|
| 400  | Bad request / missing fields |
| 401  | Unauthenticated |
| 403  | Forbidden (insufficient role) |
| 404  | Resource not found |
| 409  | Conflict (duplicate) |
| 500  | Internal server error |
