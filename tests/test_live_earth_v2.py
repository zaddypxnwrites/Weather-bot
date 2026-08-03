import unittest
import json
from app import app


class TestLiveEarthV2(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_live_earth_page_load(self):
        res = self.client.get('/live-earth')
        self.assertEqual(res.status_code, 200)

    def test_cameras_endpoint(self):
        res = self.client.get('/api/live-earth/cameras')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get('status'), 'success')
        self.assertGreaterEqual(data.get('count', 0), 50)

    def test_satellites_12_layers(self):
        res = self.client.get('/api/live-earth/satellites')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data.get('count'), 12)

    def test_earth_imagery_providers(self):
        res = self.client.get('/api/live-earth/earth-imagery')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get('status'), 'success')
        self.assertGreaterEqual(data.get('count', 0), 8)

    def test_events_endpoint(self):
        res = self.client.get('/api/live-earth/events')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('events', data)

    def test_radar_timeline(self):
        res = self.client.get('/api/live-earth/radar-timeline')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('timeline', data)

    def test_reverse_geocode(self):
        res = self.client.get('/api/live-earth/reverse-geocode?lat=6.5244&lon=3.3792')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('location', data)

    def test_weather_card_by_coords(self):
        res = self.client.get('/api/live-earth/weather?lat=51.5074&lon=-0.1278')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('weather', data)


if __name__ == '__main__':
    unittest.main()
