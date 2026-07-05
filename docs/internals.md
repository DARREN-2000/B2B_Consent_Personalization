# Internal Architecture

## The Request Pipeline

ConsentHub utilizes Flask's request lifecycle to enforce security globally.

1. **Routing:** Blueprints defined in `backend/app/api/` map HTTP methods to specific controller functions.
2. **Pre-processing:** The `@jwt_required()` decorator intercepts the request, decodes the JWT, and attaches the payload to the Flask global `g` context.
3. **Authorization:** The `@require_role()` decorator subsequently checks `g.user_role` against the permitted roles for that endpoint.
4. **Execution:** The controller delegates complex logic to the Model layer or utility functions.
5. **Response:** Data is serialized to JSON. Errors are caught globally and formatted into standard JSON envelopes.

## Database Interaction

SQLAlchemy 2.0 is utilized for ORM mapping. All models inherit from a declarative base.

### Tenant Scoping Pattern
To prevent cross-tenant data leakage, queries are typically constructed as:
```python
ConsentRecord.query.filter_by(organization_id=current_org_id, ...)
```
This explicit filtering is enforced in all API controllers.
