import unittest
from starlette.testclient import TestClient
from main import app
from services.firebase_service import create_user_account, get_slots_for_date, get_all_slots_for_date_admin

class TestRBACAndCustomSlots(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app, follow_redirects=False)
        # Create test user accounts
        create_user_account("malik@ubh.com", "pass123", role="artist_admin", artist_slug="malik-rose")

    def test_artist_login_and_rbac_restrictions(self):
        # 1. Login as Malik Rose (artist_admin)
        res_login = self.client.post("/admin/login", data={
            "email": "malik@ubh.com",
            "password": "pass123"
        })
        self.assertEqual(res_login.status_code, 303)

        # 2. Artist Admin accesses /admin?tab=slots -> Auto redirected to posts tab or restricted
        res_slots = self.client.get("/admin?tab=slots")
        self.assertEqual(res_slots.status_code, 200)
        self.assertNotIn("ADD CUSTOM TIME SLOT FOR DATE", res_slots.text)
        self.assertNotIn("TOTAL REGISTERED SUBSCRIBERS", res_slots.text)
        self.assertIn("ARTIST PORTAL (MALIK-ROSE)", res_slots.text)

        # 3. Artist Admin attempts Super Admin action (e.g. create custom slot) -> Blocked (303 Redirect /error)
        res_add_slot = self.client.post("/admin/slots/add-custom", data={
            "date": "2026-11-11",
            "time_label": "Unauthorized Slot",
            "duration": "2",
            "price": "100"
        })
        self.assertEqual(res_add_slot.status_code, 303)
        self.assertIn("error=Unauthorized", res_add_slot.headers.get("location"))

        # 4. Artist Admin publishes post for Malik Rose
        res_post = self.client.post("/admin/posts/add", data={
            "title": "Malik Field Note",
            "body": "Dispatch from Malik Rose."
        })
        self.assertEqual(res_post.status_code, 303)

        # Verify post appears in artist feed
        res_feed = self.client.get("/admin?tab=posts")
        self.assertIn("Malik Field Note", res_feed.text)

    def test_super_admin_custom_slots_and_bulk_wipe(self):
        # 1. Login as Super Admin
        self.client.post("/admin/login", data={"key": "[REDACTED_ADMIN_SECRET]"})

        test_date = "2026-10-31"

        # 2. Add custom time slot
        res_custom = self.client.post("/admin/slots/add-custom", data={
            "date": test_date,
            "time_label": "Midnight Vocal Lock (12:00 AM – 3:00 AM)",
            "duration": "3",
            "price": "150"
        })
        self.assertEqual(res_custom.status_code, 303)

        slots = get_slots_for_date(test_date)
        self.assertTrue(any(s["time_label"] == "Midnight Vocal Lock (12:00 AM – 3:00 AM)" for s in slots))

        # 3. Block entire day
        res_block = self.client.post("/admin/slots/block-day", data={"date": test_date})
        self.assertEqual(res_block.status_code, 303)

        slots_blocked = get_all_slots_for_date_admin(test_date)
        self.assertEqual(len(slots_blocked), 1)
        self.assertEqual(slots_blocked[0]["status"], "maintenance")

        # 4. Wipe all slots for date
        res_wipe = self.client.post("/admin/slots/wipe-day", data={"date": test_date})
        self.assertEqual(res_wipe.status_code, 303)

        slots_wiped = get_slots_for_date(test_date)
        self.assertEqual(len(slots_wiped), 0)

if __name__ == "__main__":
    unittest.main()
