import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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

def test_get_incidents():
    response = client.get("/incidents")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data

def test_invalid_status_transition():
    # First create one
    response = client.post("/incidents", json={
        "title": "Test Invalid Transition",
        "severity": "Low",
        "reported_by": "User"
    })
    incident_id = response.json()["data"]["id"]
    
    # Try invalid transition Open -> Closed
    res = client.patch(f"/incidents/{incident_id}/status", json={"status": "Closed"})
    assert res.status_code == 400
    assert "Invalid transition" in res.json()["detail"]

def test_valid_status_transition():
    # First create one
    response = client.post("/incidents", json={
        "title": "Test Valid Transition",
        "severity": "Medium",
        "reported_by": "User"
    })
    incident_id = response.json()["data"]["id"]
    
    # Try valid transition Open -> Investigating
    res = client.patch(f"/incidents/{incident_id}/status", json={"status": "Investigating"})
    assert res.status_code == 200
    assert res.json()["success"] is True
