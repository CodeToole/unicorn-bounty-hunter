"""Comprehensive test script verifying Admin Booking Deletion and Date Dropdown alignment in-memory."""
import unittest
from starlette.testclient import TestClient
from main import app

class TestAdminDeleteAndCalendar(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        # Authenticate admin session
        self.client.post("/admin/login", data={"key": "shadowurameshi2026"})

    def test_admin_delete_and_calendar_flow(self):
        test_date = "2026-12-25"
        slot_id = f"{test_date}-slot-1"

        # 1. Verify Date Selector dropdown & SSE trigger in /booking
        r_book = self.client.get("/booking")
        self.assertEqual(r_book.status_code, 200)
        self.assertIn('<select', r_book.text)
        self.assertIn('id="booking-date-select"', r_book.text)
        self.assertIn('data-on-change="$$get(\'/sse/available-slots', r_book.text)

        # 2. Verify SSE available slots endpoint
        r_sse = self.client.get(f"/sse/available-slots?booking_date={test_date}")
        self.assertEqual(r_sse.status_code, 200)
        self.assertIn("datastar-merge-fragments", r_sse.text)

        # 3. Simulate customer booking slot via checkout simulator
        r_create = self.client.post("/booking/create-checkout", data={
            "slot_id": slot_id,
            "artist_name": "VIP Rapper",
            "artist_email": "vip@music.com",
            "package_type": "podcast_bundle",
            "session_notes": "Live freestyle & interview"
        }, follow_redirects=False)
        self.assertEqual(r_create.status_code, 303)

        r_complete = self.client.post("/booking/mock-complete", data={
            "slot_id": slot_id,
            "artist_name": "VIP Rapper",
            "artist_email": "vip@music.com",
            "session_id": "sess-vip-123",
            "package_type": "podcast_bundle",
            "package_name": "Podcast + Musical Chairs Bundle"
        }, follow_redirects=False)
        self.assertEqual(r_complete.status_code, 303)

        # 4. View Admin Studio Slots Tab and check for Booked Details & Delete Button
        r_admin_slots = self.client.get(f"/admin?tab=slots&date={test_date}")
        self.assertIn("VIP Rapper", r_admin_slots.text)
        self.assertIn("vip@music.com", r_admin_slots.text)
        self.assertIn("Clear / Delete Booking", r_admin_slots.text)

        # 5. Execute Delete / Clear Booking via POST /admin/slots/delete
        r_delete = self.client.post("/admin/slots/delete", data={
            "slot_id": slot_id,
            "date": test_date
        }, follow_redirects=False)
        self.assertEqual(r_delete.status_code, 303)

        # 6. Check admin UI after deletion: Slot is back to AVAILABLE and customer info is gone
        r_admin_after = self.client.get(f"/admin?tab=slots&date={test_date}")
        self.assertIn("AVAILABLE", r_admin_after.text)
        self.assertNotIn("VIP Rapper", r_admin_after.text)

        # 7. Check public booking widget: Slot is open for booking again!
        r_public_after = self.client.get(f"/sse/available-slots?booking_date={test_date}")
        self.assertIn(slot_id, r_public_after.text)

if __name__ == "__main__":
    unittest.main()
