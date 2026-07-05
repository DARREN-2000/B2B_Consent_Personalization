# Troubleshooting

This guide addresses common issues encountered when deploying or operating ConsentHub.

## Database Connection Failures

**Symptom:** Backend container crashes on startup with `sqlalchemy.exc.OperationalError`.

**Diagnosis:** The backend cannot reach the PostgreSQL database.
**Resolution:**
1. Ensure the `DATABASE_URL` environment variable is correctly formatted: `postgresql://user:password@hostname:5432/dbname`.
2. If using Docker Compose, verify the `db` service is healthy and the `backend` service `depends_on` the database.
3. Check network policies or firewalls blocking port 5432.

## API Returns 401 Unauthorized

**Symptom:** Valid API requests unexpectedly return `401 Unauthorized`.

**Diagnosis:** JWT configuration mismatch or token expiration.
**Resolution:**
1. Check if the access token has expired. Your client should catch `401` errors and attempt a `/api/auth/refresh` call.
2. Verify that the `JWT_SECRET_KEY` environment variable matches across all backend instances. If running multiple replicas without a shared secret, tokens minted by one instance will be rejected by others.

## Cross-Origin Resource Sharing (CORS) Errors

**Symptom:** Browser console shows CORS policy blocks when the frontend attempts to call the API.

**Diagnosis:** The API is rejecting the Origin header of the frontend application.
**Resolution:**
1. Update the `CORS_ORIGINS` environment variable on the backend to include the exact protocol, domain, and port of your frontend (e.g., `https://dashboard.yourdomain.com`).
2. Ensure no trailing slashes are present in the origin string.

## Helm Deployment Stuck in Pending

**Symptom:** Pods remain in a `Pending` state indefinitely after `helm install`.

**Diagnosis:** Insufficient cluster resources or PVC provisioning failure.
**Resolution:**
1. Run `kubectl describe pod <pod-name> -n consenthub` and look at the Events section.
2. If the issue is related to PersistentVolumeClaims (PVCs) for PostgreSQL, verify your cluster has a default StorageClass configured.
3. If the issue is CPU/Memory, adjust the resource requests in the `values.yaml` file.