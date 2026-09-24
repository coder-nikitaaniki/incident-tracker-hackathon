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
    # Setup runs before each test
    conn = get_db_connection()
    yield
    # Cleanup after test
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
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Test Incident"
    assert data["data"]["status"] == "Open"

def test_validation_error_format():
    response = client.post("/incidents", json={
        "title": "   ", # Invalid empty title
        "severity": "InvalidSeverity",
        "reported_by": "User"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "error" in data

def test_get_incidents():
    client.post("/incidents", json={"title": "Test", "severity": "Low", "reported_by": "User"})
    response = client.get("/incidents")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "data" in response.json()

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

def test_delete_incident():
    create_res = client.post("/incidents", json={"title": "Test", "severity": "Low", "reported_by": "User"})
    incident_id = create_res.json()["data"]["id"]
    
    del_res = client.delete(f"/incidents/{incident_id}")
    assert del_res.status_code == 200
    
    get_res = client.get(f"/incidents/{incident_id}")
    assert get_res.status_code == 404

def test_invalid_status_transition():
    create_res = client.post("/incidents", json={"title": "Test", "severity": "Low", "reported_by": "User"})
    incident_id = create_res.json()["data"]["id"]
    
    res = client.patch(f"/incidents/{incident_id}/status", json={"status": "Closed", "actor": "Test"})
    assert res.status_code == 400
    assert "Invalid transition" in res.json()["error"]
