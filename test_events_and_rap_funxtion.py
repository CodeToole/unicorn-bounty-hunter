import re
import unittest
from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token

class TestEventsAndRapFunxtion(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.client.cookies.set("ubh_admin_session", get_session_token())

    def test_events_and_rap_funxtion_flow(self):
        # 1. Verify /rap-funxtion displays COMING SOON
        r_rf = self.client.get("/rap-funxtion")
        self.assertEqual(r_rf.status_code, 200)
        self.assertIn("STATUS: COMING SOON", r_rf.text)
        self.assertIn("lineup configurations are currently being finalized", r_rf.text)
        self.assertNotIn("RESCHEDULING IN PROGRESS", r_rf.text)

        # 2. Verify Admin Events Tab
        r_admin_events = self.client.get("/admin?tab=events")
        self.assertEqual(r_admin_events.status_code, 200)
        self.assertIn("Rap Funxtion", r_admin_events.text)
        self.assertIn("Delete Event", r_admin_events.text)

        # 3. Add a temporary event to test creation and deletion
        r_add = self.client.post("/admin/events/add", data={
            "title": "Rap Funxtion 17 Winter Showcase",
            "date": "December 2026",
            "status": "Tickets Live",
            "flyer_url": "/static/assets/rf16_flyer_new.jpg",
            "ticket_url": "https://tickets.example.com",
            "description": "Exclusive winter headline showcase featuring full roster."
        }, follow_redirects=False)
        self.assertEqual(r_add.status_code, 303)

        # 4. Verify public /rap-funxtion reflects new live event
        r_rf_new = self.client.get("/rap-funxtion")
        self.assertIn("RAP FUNXTION 17 WINTER SHOWCASE", r_rf_new.text)
        self.assertIn("STATUS: TICKETS LIVE", r_rf_new.text)

        # 5. Extract event ID from admin events list and delete it
        r_admin_list = self.client.get("/admin?tab=events")
        match = re.search(r'name="event_id"\s+value="([^"]+)"', r_admin_list.text)
        self.assertIsNotNone(match)
        event_id_to_delete = match.group(1)

        r_delete = self.client.post("/admin/events/delete", data={
            "event_id": event_id_to_delete
        }, follow_redirects=False)
        self.assertEqual(r_delete.status_code, 303)

        # 6. Verify /rap-funxtion reverted back to COMING SOON
        r_rf_final = self.client.get("/rap-funxtion")
        self.assertIn("STATUS: COMING SOON", r_rf_final.text)

if __name__ == "__main__":
    unittest.main()
