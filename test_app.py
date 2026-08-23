import unittest
import datetime
from starlette.testclient import TestClient
from routes.admin import extract_youtube_id
from services.firebase_service import (
    get_slots_for_date,
    get_slot_by_id,
    update_slot_status,
    add_subscriber,
    get_subscribers,
    add_event,
    get_events,
    add_showcase,
    get_showcases
)
from services.stripe_service import create_checkout_session, process_successful_payment
from main import app

class TestUBHPlatform(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_youtube_regex(self):
        cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("https://youtu.be/dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("https://www.youtube.com/playlist?list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1", ("videoseries?list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1", True)),
        ]
        for url, expected in cases:
            res = extract_youtube_id(url)
            self.assertEqual(res, expected, f"Failed on URL: {url}")
        print("[OK] YouTube regex parsing tests passed.")

    def test_firebase_service(self):
        today = datetime.date.today().isoformat()
        slots = get_slots_for_date(today)
        self.assertTrue(len(slots) > 0)
        first_slot = slots[0]
        self.assertEqual(first_slot["status"], "available")

        # Test status update
        update_slot_status(first_slot["id"], "booked", "Test Artist", "test@artist.com")
        updated = get_slot_by_id(first_slot["id"])
        self.assertEqual(updated["status"], "booked")
        self.assertEqual(updated["artist_name"], "Test Artist")

        # Reset slot
        update_slot_status(first_slot["id"], "available")

        # Subscribers
        test_email = "test-hunt@ubh.com"
        self.assertTrue(add_subscriber(test_email))
        subs = get_subscribers()
        self.assertTrue(any(s["email"] == test_email for s in subs))

        # Events
        ev = add_event("Rap Funxtion Test", "Dec 2026", "Scheduled", "/static/assets/rf16_flyer_new.jpg", "#", "Test Desc")
        self.assertEqual(ev["title"], "Rap Funxtion Test")
        self.assertTrue(len(get_events()) > 0)

        # Showcases
        sc = add_showcase("Cypher Vol 1", "dQw4w9WgXcQ", "Test Cypher")
        self.assertEqual(sc["youtube_id"], "dQw4w9WgXcQ")
        self.assertTrue(len(get_showcases()) > 0)
        print("[OK] Firebase dual-mode service tests passed.")

    def test_stripe_service_mock(self):
        today = datetime.date.today().isoformat()
        slots = get_slots_for_date(today)
        first_slot = slots[0]

        session = create_checkout_session(first_slot["id"], "Malik", "malik@test.com")
        self.assertIn("url", session)
        self.assertIn("mock-checkout", session["url"])

        # Test process payment
        process_successful_payment(first_slot["id"], "Malik", "malik@test.com")
        slot = get_slot_by_id(first_slot["id"])
        self.assertEqual(slot["status"], "booked")

        # Reset
        update_slot_status(first_slot["id"], "available")
        print("[OK] Stripe checkout session generation tests passed.")

    def test_routes_endpoints(self):
        endpoints = [
            ("/", 200),
            ("/services", 200),
            ("/showcase", 200),
            ("/musical-chairs", 200),
            ("/rap-funxtion", 200),
            ("/music", 200),
            ("/merch", 200),
            ("/booking", 200),
            ("/health", 200),
            ("/admin", 200),
            ("/admin?key=[REDACTED_ADMIN_SECRET]", 200),
        ]
        for path, expected_status in endpoints:
            response = self.client.get(path)
            self.assertEqual(response.status_code, expected_status, f"Failed on {path}: {response.status_code}")
        print("[OK] Public and Admin route endpoint tests passed.")

    def test_sse_endpoint(self):
        today = datetime.date.today().isoformat()
        response = self.client.get(f"/sse/available-slots?booking_date={today}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers.get("content-type", ""))
        self.assertIn("datastar-merge-fragments", response.text)
        self.assertIn("slot-container", response.text)
        print("[OK] Datastar SSE streaming endpoint test passed.")

    def test_email_subscription_api(self):
        response = self.client.post("/subscribe", data={"email": "newfan@ubh.com"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        print("[OK] Email subscription API test passed.")

if __name__ == "__main__":
    unittest.main()
