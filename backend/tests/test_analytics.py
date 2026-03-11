"""Tests for analytics endpoints."""


def _create_policy_and_records(client, headers, org_id, n=5):
    """Helper: create a policy and n records."""
    resp = client.post("/api/consents/policies", json={
        "organization_id": org_id,
        "name": "Analytics Policy",
        "policy_type": "gdpr",
    }, headers=headers)
    policy_id = resp.json["id"]
    for i in range(n):
        status = "granted" if i % 2 == 0 else "denied"
        client.post("/api/consents/records", json={
            "policy_id": policy_id,
            "data_subject_id": f"sub-{i}",
            "status": status,
        }, headers=headers)
    return policy_id


class TestAnalytics:
    def test_summary(self, client, auth_headers, org):
        _create_policy_and_records(client, auth_headers, org["id"])
        resp = client.get("/api/analytics/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json
        assert "total_records" in data
        assert "consent_rate_pct" in data
        assert "by_status" in data

    def test_trends(self, client, auth_headers, org):
        _create_policy_and_records(client, auth_headers, org["id"])
        resp = client.get("/api/analytics/trends?days=7", headers=auth_headers)
        assert resp.status_code == 200
        assert "trends" in resp.json
        assert resp.json["days"] == 7

    def test_platform_overview_admin_only(self, client, auth_headers):
        resp = client.get("/api/analytics/overview", headers=auth_headers)
        assert resp.status_code == 200
        assert "organizations" in resp.json
        assert "users" in resp.json

    def test_requires_auth(self, client):
        resp = client.get("/api/analytics/summary")
        assert resp.status_code == 401
