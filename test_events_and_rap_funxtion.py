import os
import io
import re
import unittest
from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token
from services.firebase_service import _reset_local_stores, get_dispatches, get_events

class TestEventsAndRapFunxtion(unittest.TestCase):

    def setUp(self):
        _reset_local_stores()
        self.client = TestClient(app)
        self.client.cookies.set("ubh_admin_session", get_session_token())

    def tearDown(self):
        _reset_local_stores()
        upload_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
        if os.path.exists(upload_dir):
            for f in os.listdir(upload_dir):
                if f.startswith("test_flyer_"):
                    try:
                        os.remove(os.path.join(upload_dir, f))
                    except Exception:
                        pass

    def test_rap_funxtion_dispatch_feed(self):
        # 1. Verify /rap-funxtion displays dispatches feed
        r_rf = self.client.get("/rap-funxtion")
        self.assertEqual(r_rf.status_code, 200)
        self.assertIn("RAP FUNXTION DISPATCHES", r_rf.text)
        self.assertIn("Musical Chairs Cypher Vol. 1", r_rf.text)
        self.assertIn("Ali Kazem", r_rf.text)
        self.assertIn("CYPHER", r_rf.text)

    def test_rap_funxtion_watch_player(self):
        # 2. Verify /rap-funxtion/watch/{id} renders player and increments views
        seed_dispatch = get_dispatches()[0]
        seed_id = seed_dispatch["id"]
        initial_views = seed_dispatch.get("views", 0)

        r_watch = self.client.get(f"/rap-funxtion/watch/{seed_id}")
        self.assertEqual(r_watch.status_code, 200)
        self.assertIn("Musical Chairs Cypher Vol. 1", r_watch.text)
        self.assertIn("iframe", r_watch.text.lower())
        self.assertIn("NEXT DISPATCHES", r_watch.text)

        # 3. Verify 404 behavior for invalid dispatch ID
        r_invalid = self.client.get("/rap-funxtion/watch/nonexistent-dispatch-id")
        self.assertEqual(r_invalid.status_code, 200)
        self.assertIn("DISPATCH NOT FOUND", r_invalid.text)

    def test_admin_dispatches_rbac(self):
        # 4. Super Admin can view dispatches tab
        r_admin = self.client.get("/admin?tab=dispatches")
        self.assertEqual(r_admin.status_code, 200)
        self.assertIn("FAST DISPATCH PUBLISHER", r_admin.text)
        self.assertIn("LIVE DISPATCHES", r_admin.text)

        # 5. Ali Kazem (Council Artist Admin) can view dispatches tab
        ali_client = TestClient(app)
        ali_client.cookies.set("ubh_admin_session", "artist_admin:ali-kazem:ali@ubh.com")
        r_ali = ali_client.get("/admin?tab=dispatches")
        self.assertEqual(r_ali.status_code, 200)
        self.assertIn("FAST DISPATCH PUBLISHER", r_ali.text)

        # 6. Other Artist Admin (e.g. marv-k-z) cannot access dispatches tab (defaults to posts)
        marv_client = TestClient(app)
        marv_client.cookies.set("ubh_admin_session", "artist_admin:marv-k-z:marv@ubh.com")
        r_marv = marv_client.get("/admin?tab=dispatches")
        self.assertEqual(r_marv.status_code, 200)
        self.assertNotIn("FAST DISPATCH PUBLISHER", r_marv.text)
        self.assertIn("ARTIST PORTAL (MARV-K-Z)", r_marv.text)

    def test_admin_dispatch_crud_flow(self):
        # 7. Add a new dispatch as Super Admin
        r_add = self.client.post("/admin/dispatches/add", data={
            "title": "Rat Trap Underground Cypher Vol. 2",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_tag": "Cypher",
            "thumbnail_url": ""
        }, follow_redirects=False)
        self.assertEqual(r_add.status_code, 303)
        self.assertIn("msg=Dispatch+published+successfully", r_add.headers["location"])

        # 8. Verify public /rap-funxtion displays newly published dispatch
        r_rf = self.client.get("/rap-funxtion")
        self.assertIn("Rat Trap Underground Cypher Vol. 2", r_rf.text)

        # 9. Extract newly created dispatch ID from admin list
        r_admin_list = self.client.get("/admin?tab=dispatches")
        matches = re.findall(r'name="dispatch_id"\s+value="([^"]+)"', r_admin_list.text)
        self.assertTrue(len(matches) >= 2)
        new_dispatch_id = matches[0]

        # 10. Delete the newly created dispatch
        r_delete = self.client.post("/admin/dispatches/delete", data={
            "dispatch_id": new_dispatch_id
        }, follow_redirects=False)
        self.assertEqual(r_delete.status_code, 303)
        self.assertIn("msg=Dispatch+deleted+successfully", r_delete.headers["location"])

        # 11. Verify dispatch is removed from public feed
        r_rf_after = self.client.get("/rap-funxtion")
        self.assertNotIn("Rat Trap Underground Cypher Vol. 2", r_rf_after.text)

    def test_ali_kazem_dispatch_add_and_unauthorized_rejection(self):
        # 12. Ali Kazem can publish a dispatch
        ali_client = TestClient(app)
        ali_client.cookies.set("ubh_admin_session", "artist_admin:ali-kazem:ali@ubh.com")
        r_ali_add = ali_client.post("/admin/dispatches/add", data={
            "title": "Ali Kazem Exclusive Studio Session",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_tag": "Exclusive",
            "thumbnail_url": ""
        }, follow_redirects=False)
        self.assertEqual(r_ali_add.status_code, 303)
        self.assertIn("msg=Dispatch+published+successfully", r_ali_add.headers["location"])

        # 13. Unauthorized artist cannot publish dispatch
        marv_client = TestClient(app)
        marv_client.cookies.set("ubh_admin_session", "artist_admin:marv-k-z:marv@ubh.com")
        r_marv_add = marv_client.post("/admin/dispatches/add", data={
            "title": "Unauthorized Dispatch",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_tag": "Drop",
            "thumbnail_url": ""
        }, follow_redirects=False)
        self.assertEqual(r_marv_add.status_code, 303)
        self.assertIn("error=Unauthorized", r_marv_add.headers["location"])

    def test_events_admin_flow(self):
        # 14. Verify Admin Events tab and add/delete still works
        r_admin_events = self.client.get("/admin?tab=events")
        self.assertEqual(r_admin_events.status_code, 200)
        self.assertIn("Rap Funxtion", r_admin_events.text)
        self.assertIn("Delete Event", r_admin_events.text)

        # Add an event
        r_add = self.client.post("/admin/events/add", data={
            "title": "Rap Funxtion 17 Winter Showcase",
            "date": "December 2026",
            "status": "Tickets Live",
            "flyer_url": "/static/assets/rf16_flyer_new.jpg",
            "ticket_url": "https://tickets.example.com",
            "description": "Exclusive winter headline showcase featuring full roster."
        }, follow_redirects=False)
        self.assertEqual(r_add.status_code, 303)

        # Extract event ID and delete it
        r_admin_list = self.client.get("/admin?tab=events")
        match = re.search(r'name="event_id"\s+value="([^"]+)"', r_admin_list.text)
        self.assertIsNotNone(match)
        event_id_to_delete = match.group(1)

        r_delete = self.client.post("/admin/events/delete", data={
            "event_id": event_id_to_delete
        }, follow_redirects=False)
        self.assertEqual(r_delete.status_code, 303)

    def test_event_flyer_file_upload(self):
        # 15. Verify direct file upload for event flyer
        fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        files = {
            "flyer_file": ("test_flyer_sample.png", io.BytesIO(fake_png), "image/png")
        }
        data = {
            "title": "Uploaded Direct Flyer Event",
            "date": "Spring 2027",
            "status": "Tickets Live",
            "ticket_url": "https://tickets.example.com",
            "description": "Showcase testing direct multipart file upload."
        }

        r_upload = self.client.post("/admin/events/add", data=data, files=files, follow_redirects=False)
        self.assertEqual(r_upload.status_code, 303)
        self.assertIn("msg=Event+added+successfully", r_upload.headers["location"])

        # Verify event was saved with the uploaded flyer path
        events = get_events()
        uploaded_event = next((e for e in events if e.get("title") == "Uploaded Direct Flyer Event"), None)
        self.assertIsNotNone(uploaded_event)
        self.assertIn("flyer_url", uploaded_event)
        self.assertIn("flyer_image_url", uploaded_event)
        self.assertTrue(
            uploaded_event["flyer_url"].startswith("/static/uploads/test_flyer_sample_") or
            "storage.googleapis.com" in uploaded_event["flyer_url"]
        )

        # Verify admin tab displays the uploaded flyer image
        r_admin = self.client.get("/admin?tab=events")
        self.assertEqual(r_admin.status_code, 200)
        self.assertIn("Uploaded Direct Flyer Event", r_admin.text)
        self.assertIn(uploaded_event["flyer_url"], r_admin.text)

if __name__ == "__main__":
    unittest.main()
