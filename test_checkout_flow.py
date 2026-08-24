import unittest
import datetime
from unittest.mock import patch
from starlette.testclient import TestClient
from main import app

class TestCheckoutFlow(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_checkout_and_packages(self):
        ts = int(datetime.datetime.now().timestamp())
        slot_studio = f"2026-10-01-{ts}-slot-1"
        slot_podcast = f"2026-10-02-{ts}-slot-2"
        slot_bundle = f"2026-10-03-{ts}-slot-3"

        r1 = self.client.get("/booking")
        self.assertEqual(r1.status_code, 200)
        self.assertIn("Studio Recording Session", r1.text)
        self.assertIn("Shadow Talk Podcast", r1.text)

        r2 = self.client.get("/services")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("Shadow Talk Podcast", r2.text)

        r3 = self.client.post("/booking/create-checkout", data={}, follow_redirects=False)
        self.assertEqual(r3.status_code, 303)
        self.assertIn("error=", r3.headers.get("location", ""))

        r4 = self.client.post("/booking/create-checkout", data={"slot_id": slot_studio}, follow_redirects=False)
        self.assertEqual(r4.status_code, 303)
        self.assertIn("error=", r4.headers.get("location", ""))

        r5 = self.client.post("/booking/create-checkout", data={"slot_id": "nonexistent-slot-999", "artist_name": "Test Artist", "artist_email": "test@domain.com"}, follow_redirects=False)
        self.assertEqual(r5.status_code, 303)
        self.assertIn("error=", r5.headers.get("location", ""))

        with patch("config.STRIPE_SECRET_KEY", "sk_test_mock_key"), \
             patch("services.stripe_service.STRIPE_SECRET_KEY", "sk_test_mock_key"), \
             patch("services.stripe_service.is_mock_payment_allowed", return_value=True), \
             patch("routes.booking.is_mock_payment_allowed", return_value=True):
            r6 = self.client.post("/booking/create-checkout", data={
                "slot_id": slot_studio,
                "artist_name": "Ali Kazem",
                "artist_email": "ali@ubh.com",
                "package_type": "studio",
                "phone_number": "555-1234",
                "session_notes": "Vocal stems review"
            }, follow_redirects=False)
            self.assertEqual(r6.status_code, 303)
            self.assertIn("/booking/mock-checkout", r6.headers.get("location", ""))
            self.assertIn("price=100", r6.headers.get("location", ""))

            r7 = self.client.post("/booking/create-checkout", data={
                "slot_id": slot_podcast,
                "artist_name": "Special Guest",
                "artist_email": "guest@podcast.com",
                "package_type": "podcast_standard",
                "phone_number": "555-9876",
                "session_notes": "Album rollout interview"
            }, follow_redirects=False)
            self.assertEqual(r7.status_code, 303)
            self.assertIn("/booking/mock-checkout", r7.headers.get("location", ""))
            self.assertIn("price=50", r7.headers.get("location", ""))

            r8 = self.client.post("/booking/create-checkout", data={
                "slot_id": slot_bundle,
                "artist_name": "Cypher Star",
                "artist_email": "cypher@ubh.com",
                "package_type": "podcast_bundle",
                "session_notes": "Live verse & interview"
            }, follow_redirects=False)
            self.assertEqual(r8.status_code, 303)
            self.assertIn("/booking/mock-checkout", r8.headers.get("location", ""))
            self.assertIn("price=100", r8.headers.get("location", ""))

            r9 = self.client.get(f"/booking/mock-checkout?session_id=mock-123&slot_id={slot_bundle}&artist=Cypher%20Star&email=cypher@ubh.com&price=100&package=podcast_bundle&package_name=Shadow%20Talk%20Podcast%20%2B%20Musical%20Chairs%20Bundle")
            self.assertEqual(r9.status_code, 200)
            self.assertIn("COMPLETE RESERVATION", r9.text)
            self.assertIn("$100 USD", r9.text)

            r10 = self.client.post("/booking/mock-complete", data={
                "slot_id": slot_bundle,
                "artist_name": "Cypher Star",
                "artist_email": "cypher@ubh.com",
                "session_id": "mock-sess-999",
                "package_type": "podcast_bundle",
                "package_name": "Shadow Talk Podcast + Musical Chairs Bundle"
            }, follow_redirects=False)
            self.assertEqual(r10.status_code, 303)
            self.assertIn("/booking/success", r10.headers.get("location", ""))

        r11 = self.client.get(f"/booking/success?mock=true&session_id=mock-sess-999&slot_id={slot_bundle}&artist=Cypher%20Star&package_name=Shadow%20Talk%20Podcast%20%2B%20Musical%20Chairs%20Bundle")
        self.assertEqual(r11.status_code, 200)
        self.assertIn("BOOKING LOCKED IN", r11.text)

if __name__ == "__main__":
    unittest.main()
