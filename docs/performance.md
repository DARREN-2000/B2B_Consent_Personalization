# Performance Characteristics

ConsentHub is designed for low-latency, high-throughput consent tracking.

## API Layer
The Flask backend operates statelessly. The primary constraint on throughput is database connection pooling and CPU utilization. Performance scales linearly with the addition of replica pods via the Kubernetes Horizontal Pod Autoscaler.

## Database
Read-heavy analytical queries (`GET /analytics/summary`) are the most resource-intensive operations. For datasets exceeding 1M records, it is recommended to ensure appropriate indexing on the `organization_id`, `policy_id`, and `status` columns in PostgreSQL.

## Frontend
The dashboard is a static SPA. Load time is entirely dependent on CDN edge caching and client bandwidth, as there is zero server-side rendering latency.
