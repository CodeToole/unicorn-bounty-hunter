import unittest
from starlette.testclient import TestClient
from main import app

class TestEventsAndRapFunxtion(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.client.post("/admin/login", data={"key": "shadowurameshi2026"})

    def test_events_and_rap_funxtion_flow(self):
        r_rf = self.client.get("/rap-funxtion")
        self.assertEqual(r_rf.status_code, 200)

        r_admin_events = self.client.get("/admin?tab=events")
        self.assertEqual(r_admin_events.status_code, 200)

if __name__ == "__main__":
    unittest.main()
