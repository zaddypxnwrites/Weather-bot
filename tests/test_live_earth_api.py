import unittest
from app import app


class TestLiveEarthAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_live_earth_index_route(self):
        response = self.app.get("/live-earth")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Live Earth", response.data)

    def test_api_cameras_all(self):
        response = self.app.get("/api/live-earth/cameras")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("cameras", json_data)

    def test_api_cameras_spatial_query(self):
        response = self.app.get("/api/live-earth/cameras?lat=6.5244&lon=3.3792&radius=500")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("cameras", json_data)


if __name__ == "__main__":
    unittest.main()
