import pytest
import os
from fastapi.testclient import TestClient

# Set testing DB
os.environ["DB_FILE"] = "test_incident_tracker.db"

from main import app
from database import get_db_connection

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    conn = get_db_connection()
    yield
    conn.close()
    if os.path.exists("test_incident_tracker.db"):
        os.remove("test_incident_tracker.db")

def test_create_incident():
    response = client.post("/incidents", json={
        "title": "Test Incident",
        "description": "Test Description",
        "severity": "High",
        "reported_by": "TestUser"
    })
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["data"]["title"] == "Test Incident"

def test_validation_error_format():
    response = client.post("/incidents", json={
        "title": "   ",
        "severity": "InvalidSeverity",
        "reported_by": "User"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "error" in data

def test_get_incidents_and_filters():
    client.post("/incidents", json={"title": "Test 1", "severity": "Low", "reported_by": "U1"})
    client.post("/incidents", json={"title": "Test 2", "severity": "Critical", "reported_by": "U2"})
    
    response = client.get("/incidents")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    
    # Test filters
    res_filtered = client.get("/incidents?severity=Critical")
    assert res_filtered.json()["total"] == 1
    assert res_filtered.json()["data"][0]["severity"] == "Critical"

    # Test sorting
    res_sort = client.get("/incidents?sort_by=severity&order=desc")
    # Low should be at bottom, Critical at top
    assert res_sort.json()["data"][0]["severity"] == "Critical"
    assert res_sort.json()["data"][1]["severity"] == "Low"

def test_get_incident_404():
    response = client.get("/incidents/999")
    assert response.status_code == 404
    assert response.json()["success"] is False

def test_put_incident():
    create_res = client.post("/incidents", json={"title": "Test", "severity": "Low", "reported_by": "User"})
    incident_id = create_res.json()["data"]["id"]
    
    put_res = client.put(f"/incidents/{incident_id}", json={
        "title": "Updated Title",
        "severity": "Critical",
        "assigned_to": "DevTeam"
    })
    assert put_res.status_code == 200
    assert put_res.json()["data"]["title"] == "Updated Title"
    assert put_res.json()["data"]["assigned_to"] == "DevTeam"

    put_404 = client.put("/incidents/999", json={"title": "T", "severity": "Low", "reported_by": "User"})
    assert put_404.status_code == 404

def test_delete_incident_and_cascade():
    create_res = client.post("/incidents", json={"title": "Test", "severity": "Low", "reported_by": "User"})
    incident_id = create_res.json()["data"]["id"]
    
    # Check audit log exists
    audit_res = client.get(f"/incidents/{incident_id}/audit-log")
    assert len(audit_res.json()["data"]) == 1
    
    del_res = client.delete(f"/incidents/{incident_id}")
    assert del_res.status_code == 200
    
    # Check cascade
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM incident_audit_log WHERE incident_id = ?", (incident_id,))
    count = c.fetchone()[0]
    conn.close()
    assert count == 0

def test_status_transitions():
    create_res = client.post("/incidents", json={"title": "Test", "severity": "Low", "reported_by": "User"})
    incident_id = create_res.json()["data"]["id"]
    
    # Valid Open -> Investigating
    res = client.patch(f"/incidents/{incident_id}/status", json={"status": "Investigating", "actor": "Test"})
    assert res.status_code == 200
    
    # Invalid Investigating -> Open
    res2 = client.patch(f"/incidents/{incident_id}/status", json={"status": "Open", "actor": "Test"})
    assert res2.status_code == 400
    
    # Valid Investigating -> Resolved -> Closed
    client.patch(f"/incidents/{incident_id}/status", json={"status": "Resolved", "actor": "Test"})
    client.patch(f"/incidents/{incident_id}/status", json={"status": "Closed", "actor": "Test"})
    
    get_res = client.get(f"/incidents/{incident_id}")
    assert get_res.json()["data"]["status"] == "Closed"
