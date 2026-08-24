import unittest
from starlette.testclient import TestClient
from main import app

class TestCheckoutFlow(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_checkout_and_packages(self):
        r1 = self.client.get("/booking")
        self.assertEqual(r1.status_code, 200)

        r2 = self.client.post("/booking/create-checkout", data={
            "slot_id": "test-slot-1",
            "artist_name": "Test Artist",
            "artist_email": "artist@test.com",
            "package_type": "studio",
            "session_notes": "Vocals tracking"
        }, follow_redirects=False)
        self.assertEqual(r2.status_code, 303)

if __name__ == "__main__":
    unittest.main()
