import unittest
from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token

class TestLiveRoutesInProcess(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.client.cookies.set("ubh_admin_session", get_session_token())

    def test_live_routes(self):
        routes = [
            '/',
            '/services',
            '/showcase',
            '/musical-chairs',
            '/rap-funxtion',
            '/music',
            '/merch',
            '/booking',
            '/admin',
            '/admin?tab=slots',
            '/admin?tab=showcases',
            '/admin?tab=events',
            '/admin?tab=posts',
            '/admin?tab=subscribers',
            '/health'
        ]
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} failed with status {res.status_code}")

    def test_sse_streaming(self):
        sse_res = self.client.get('/sse/available-slots?booking_date=2026-08-25')
        self.assertEqual(sse_res.status_code, 200)
        self.assertIn("datastar-merge-fragments", sse_res.text)
        self.assertIn("slot-container", sse_res.text)

    def test_subscribe_api(self):
        sub_res = self.client.post('/subscribe', data={'email': 'livecheck@ubh.com'})
        self.assertEqual(sub_res.status_code, 200)
        self.assertTrue(sub_res.json().get('success'))

if __name__ == "__main__":
    unittest.main()
