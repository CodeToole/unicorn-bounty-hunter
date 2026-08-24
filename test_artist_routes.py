import unittest
from starlette.testclient import TestClient
from main import app

class TestArtistRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.client.post("/admin/login", data={"key": "shadowurameshi2026"})

    def test_artist_routes_and_profiles(self):
        routes = [
            ("/", 200),
            ("/roster", 200),
            ("/roster/ali-kazem", 200),
            ("/roster/malik-rose", 200),
            ("/roster/unkn0wn", 200),
            ("/roster/yung-illie", 200),
            ("/roster/nonexistent-artist", 200),
            ("/admin?tab=posts", 200),
        ]
        for path, expected_status in routes:
            res = self.client.get(path)
            self.assertEqual(res.status_code, expected_status, f"Failed on path: {path}")

if __name__ == "__main__":
    unittest.main()
