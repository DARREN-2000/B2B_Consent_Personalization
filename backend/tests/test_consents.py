"""Tests for consent policy and record endpoints."""


def _create_policy(client, auth_headers, org_id, name="GDPR Policy", policy_type="gdpr"):
    resp = client.post("/api/consents/policies", json={
        "organization_id": org_id,
        "name": name,
        "policy_type": policy_type,
        "description": "GDPR data processing consent",
        "requires_explicit_consent": True,
        "retention_days": 365,
    }, headers=auth_headers)
    assert resp.status_code == 201, resp.json
    return resp.json


class TestPolicies:
    def test_create_policy(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        assert policy["name"] == "GDPR Policy"
        assert policy["policy_type"] == "gdpr"

    def test_list_policies(self, client, auth_headers, org):
        _create_policy(client, auth_headers, org["id"], "P1")
        _create_policy(client, auth_headers, org["id"], "P2", "ccpa")
        resp = client.get("/api/consents/policies", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json["total"] >= 2

    def test_get_policy(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        resp = client.get(f"/api/consents/policies/{policy['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json["id"] == policy["id"]

    def test_update_policy(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        resp = client.put(f"/api/consents/policies/{policy['id']}", json={
            "description": "Updated description",
            "version": "2.0",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json["version"] == "2.0"

    def test_delete_policy(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        resp = client.delete(f"/api/consents/policies/{policy['id']}", headers=auth_headers)
        assert resp.status_code == 200

    def test_create_policy_missing_fields(self, client, auth_headers):
        resp = client.post("/api/consents/policies", json={"name": "Incomplete"}, headers=auth_headers)
        assert resp.status_code == 400

    def test_requires_auth(self, client):
        resp = client.get("/api/consents/policies")
        assert resp.status_code == 401


class TestRecords:
    def test_create_record(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        resp = client.post("/api/consents/records", json={
            "policy_id": policy["id"],
            "data_subject_id": "user-123",
            "data_subject_email": "user@example.com",
            "status": "granted",
            "consent_method": "web-form",
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json["status"] == "granted"
        assert resp.json["data_subject_id"] == "user-123"

    def test_create_record_invalid_status(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        resp = client.post("/api/consents/records", json={
            "policy_id": policy["id"],
            "data_subject_id": "user-123",
            "status": "unknown",
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_list_records(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        # Create two records
        for i in range(2):
            client.post("/api/consents/records", json={
                "policy_id": policy["id"],
                "data_subject_id": f"user-{i}",
                "status": "granted",
            }, headers=auth_headers)

        resp = client.get("/api/consents/records", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json["total"] >= 2

    def test_withdraw_consent(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        record_resp = client.post("/api/consents/records", json={
            "policy_id": policy["id"],
            "data_subject_id": "withdraw-user",
            "status": "granted",
        }, headers=auth_headers)
        record_id = record_resp.json["id"]

        withdraw_resp = client.put(
            f"/api/consents/records/{record_id}/withdraw",
            headers=auth_headers,
        )
        assert withdraw_resp.status_code == 200
        assert withdraw_resp.json["status"] == "withdrawn"
        assert withdraw_resp.json["withdrawn_at"] is not None

    def test_export_csv(self, client, auth_headers, org):
        policy = _create_policy(client, auth_headers, org["id"])
        client.post("/api/consents/records", json={
            "policy_id": policy["id"],
            "data_subject_id": "export-user",
            "status": "granted",
        }, headers=auth_headers)

        resp = client.get("/api/consents/records/export?format=csv", headers=auth_headers)
        assert resp.status_code == 200
        assert "text/csv" in resp.content_type

    def test_export_json(self, client, auth_headers, org):
        resp = client.get("/api/consents/records/export?format=json", headers=auth_headers)
        assert resp.status_code == 200
        assert "application/json" in resp.content_type
