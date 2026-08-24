import unittest
from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token

class TestArtistRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.client.cookies.set("ubh_admin_session", get_session_token())

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

    def test_artist_post_and_profile_content(self):
        # Publish a test post for Ali Kazem
        res_post = self.client.post("/admin/posts/add", data={
            "artist_slug": "ali-kazem",
            "title": "Studio Field Report",
            "body": "Tracking sessions live in the acoustic room with new HS8 monitoring setup.",
            "media_url": ""
        }, follow_redirects=False)
        self.assertEqual(res_post.status_code, 303)

        # Content checks on Ali Kazem profile
        resp = self.client.get("/roster/ali-kazem")
        html = resp.text
        self.assertIn("ALI KAZEM", html)
        self.assertIn("shadowurameshi", html)
        self.assertIn("Studio Field Report", html)
        self.assertIn("navigator.share", html)
        self.assertIn("BACK TO ROSTER", html)

        # Admin Creator Portal checks
        resp2 = self.client.get("/admin?tab=posts")
        html2 = resp2.text
        self.assertIn("ARTIST CREATOR PORTAL", html2)
        self.assertIn("PUBLISH POST", html2)
        self.assertIn("Delete Post", html2)

if __name__ == "__main__":
    unittest.main()
