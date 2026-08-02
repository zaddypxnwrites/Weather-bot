import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


def test_live_earth_page():
    client = app.test_client()
    response = client.get("/live-earth")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Live Earth Platform" in html
    assert "Public Cameras" in html


def test_api_cameras_all():
    client = app.test_client()
    response = client.get("/api/live-earth/cameras")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] > 0
    assert len(data["cameras"]) > 0


def test_api_cameras_filter_category():
    client = app.test_client()
    response = client.get("/api/live-earth/cameras?category=Traffic+Cameras")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    for cam in data["cameras"]:
        assert "Traffic" in cam["category"] or "Traffic" in cam["name"]


def test_api_camera_detail_success():
    client = app.test_client()
    response = client.get("/api/live-earth/cameras/cam-london-1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["camera"]["city"] == "London"


def test_api_camera_detail_not_found():
    client = app.test_client()
    response = client.get("/api/live-earth/cameras/non-existent-cam")
    assert response.status_code == 404
    data = response.get_json()
    assert "No public live camera is available" in data["message"]


def test_api_satellites():
    client = app.test_client()
    response = client.get("/api/live-earth/satellites")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["layers"]) >= 3


def test_api_earth_imagery():
    client = app.test_client()
    response = client.get("/api/live-earth/earth-imagery")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["layers"]) >= 2


def test_api_status():
    client = app.test_client()
    response = client.get("/api/live-earth/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["connection_status"] == "Online"
    assert len(data["providers"]) > 0
