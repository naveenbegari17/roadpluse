import pytest
from app import app
from database.db import init_db, get_connection


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Roads That Speak" in response.data
    assert b"Total Reports" in response.data


def test_map_route(client):
    response = client.get("/map")
    assert response.status_code == 200
    assert b"Interactive Live Risk Map" in response.data


def test_api_reports(client):
    response = client.get("/api/reports")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert len(json_data["data"]) >= 1


def test_api_analytics(client):
    response = client.get("/api/analytics")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert "categories" in json_data["data"]
    assert "severities" in json_data["data"]


def test_report_creation_flow(client):
    # Submit a new report
    post_data = {
        "title": "Large Pothole Test Location",
        "category": "Pothole",
        "description": "Created during automated route test validation",
        "severity": "Critical",
        "location_name": "Kondapur Signal, Hyderabad",
        "latitude": "17.4600",
        "longitude": "78.3600"
    }
    response = client.post("/report", data=post_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Large Pothole Test Location" in response.data
    assert b"Road Risk Score" in response.data


def test_invalid_report_validation(client):
    # Missing required title and bad category
    post_data = {
        "title": "",
        "category": "InvalidCategory",
        "description": "",
        "severity": "UnknownSeverity",
        "location_name": "",
        "latitude": "invalid",
        "longitude": "invalid"
    }
    response = client.post("/report", data=post_data)
    assert response.status_code == 200
    assert b"Hazard title is required" in response.data


def test_admin_status_update_safeguard(client):
    # Fetch first report
    conn, _ = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM reports LIMIT 1;")
    report_id = cur.fetchone()[0]
    cur.close()
    conn.close()

    # Attempt status update without correct passkey
    bad_res = client.post(f"/report/{report_id}/update-status", data={
        "status": "Resolved",
        "admin_token": "WRONG_TOKEN"
    }, follow_redirects=True)
    assert b"Demo Admin key required" in bad_res.data

    # Valid passkey
    good_res = client.post(f"/report/{report_id}/update-status", data={
        "status": "Resolved",
        "admin_token": "DEMO_ADMIN"
    }, follow_redirects=True)
    assert b"Report status updated to &#39;Resolved&#39;" in good_res.data or b"Report status updated to 'Resolved'" in good_res.data
