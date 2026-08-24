import unittest
import datetime
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient
from routes.admin import extract_youtube_id, sanitize_media_url, sanitize_identifier, get_session_token
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
from services.stripe_service import (
    create_checkout_session,
    process_successful_payment,
    verify_webhook_event
)
from config import ADMIN_SECRET_KEY
from main import app

class TestUBHPlatform(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_youtube_regex_and_validation(self):
        cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("https://youtu.be/dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("dQw4w9WgXcQ", ("dQw4w9WgXcQ", False)),
            ("https://www.youtube.com/playlist?list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1", ("videoseries?list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1", True)),
            ("javascript:alert(1)", ("", False)),
            ("https://malicious.site/video", ("", False)),
            ("invalid_short_id", ("", False)),
            ("too_long_invalid_youtube_identifier_12345", ("", False)),
        ]
        for url, expected in cases:
            res = extract_youtube_id(url)
            self.assertEqual(res, expected, f"Failed on URL: {url}")
        print("[OK] YouTube regex parsing and strict validation tests passed.")

    def test_media_url_sanitizer(self):
        self.assertEqual(sanitize_media_url("https://example.com/image.jpg"), "https://example.com/image.jpg")
        self.assertEqual(sanitize_media_url("http://example.com/image.jpg"), "http://example.com/image.jpg")
        self.assertEqual(sanitize_media_url("/static/assets/rf16_flyer_new.jpg"), "/static/assets/rf16_flyer_new.jpg")
        self.assertEqual(sanitize_media_url("#", allow_hash=True), "#")
        
        # Rejected schemes
        self.assertEqual(sanitize_media_url("javascript:alert(1)"), "")
        self.assertEqual(sanitize_media_url("data:text/html,<script>alert(1)</script>"), "")
        self.assertEqual(sanitize_media_url("vbscript:msgbox(1)"), "")
        self.assertEqual(sanitize_media_url("/static/../etc/passwd"), "")
        self.assertEqual(sanitize_media_url(""), "")
        print("[OK] Media URL sanitizer tests passed.")

    def test_identifier_sanitizer(self):
        self.assertEqual(sanitize_identifier("2026-10-01-slot-1"), "2026-10-01-slot-1")
        self.assertEqual(sanitize_identifier("event_123_abc"), "event_123_abc")
        self.assertEqual(sanitize_identifier("post-xyz-789"), "post-xyz-789")
        self.assertEqual(sanitize_identifier("../../malicious"), "")
        self.assertEqual(sanitize_identifier("<script>"), "")
        self.assertEqual(sanitize_identifier(""), "")
        print("[OK] Identifier sanitizer tests passed.")

    def test_admin_authentication_and_cookie_session(self):
        # 1. Unauthenticated request to /admin -> Login View, NO data leaked
        res_unauth = self.client.get("/admin")
        self.assertEqual(res_unauth.status_code, 200)
        self.assertIn("UBH CMS PORTAL", res_unauth.text)
        self.assertIn("AUTHENTICATE", res_unauth.text)
        self.assertNotIn("ADMIN CMS ENGINE", res_unauth.text)
        self.assertNotIn("TOTAL SUBSCRIBERS", res_unauth.text)

        # 2. Failed login attempt
        res_fail = self.client.post("/admin/login", data={"key": "wrong_password"}, follow_redirects=False)
        self.assertEqual(res_fail.status_code, 303)
        self.assertIn("error=", res_fail.headers["location"])

        # 3. Successful login -> Sets HTTP-only cookie and redirects
        res_login = self.client.post("/admin/login", data={"key": ADMIN_SECRET_KEY}, follow_redirects=False)
        self.assertEqual(res_login.status_code, 303)
        self.assertIn("ubh_admin_session", res_login.headers.get("set-cookie", ""))

        # 4. Authenticated request using cookie -> Dashboard accessible
        client_auth = TestClient(app)
        client_auth.cookies.set("ubh_admin_session", get_session_token())
        res_auth = client_auth.get("/admin")
        self.assertEqual(res_auth.status_code, 200)
        self.assertIn("ADMIN CMS ENGINE", res_auth.text)
        self.assertIn("LOGOUT", res_auth.text)

        # 5. Logout flow
        res_logout = client_auth.get("/admin/logout", follow_redirects=False)
        self.assertEqual(res_logout.status_code, 303)
        print("[OK] Admin authentication and HTTP-only session cookie tests passed.")

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

    def test_mock_payment_endpoint_guards(self):
        # 1. In dev mode with mock keys, mock endpoints are accessible
        with patch("routes.booking.is_mock_payment_allowed", return_value=True):
            res_mock = self.client.get("/booking/mock-checkout?slot_id=test-slot&price=100")
            self.assertEqual(res_mock.status_code, 200)

        # 2. When mock payment is prohibited (production mode or live Stripe), mock endpoints return 403
        with patch("routes.booking.is_mock_payment_allowed", return_value=False):
            res_mock_blocked = self.client.get("/booking/mock-checkout?slot_id=test-slot&price=100")
            self.assertEqual(res_mock_blocked.status_code, 403)
            self.assertIn("disabled", res_mock_blocked.text)

            res_complete_blocked = self.client.post("/booking/mock-complete", data={"slot_id": "test-slot"})
            self.assertEqual(res_complete_blocked.status_code, 403)
            self.assertIn("disabled", res_complete_blocked.text)
        print("[OK] Mock payment lockdown & 403 guard tests passed.")

    def test_production_webhook_verification(self):
        # In production mode, unsigned payload MUST be rejected (returns None)
        with patch("services.stripe_service.IS_PRODUCTION", True):
            with patch("services.stripe_service.STRIPE_WEBHOOK_SECRET", "whsec_live_secret_key"):
                res_unsigned = verify_webhook_event(b'{"type": "checkout.session.completed"}', "")
                self.assertIsNone(res_unsigned)
        print("[OK] Production Stripe webhook signature enforcement tests passed.")

    def test_homepage_news_carousel(self):
        from services.firebase_service import add_artist_post, delete_artist_post
        post = add_artist_post("ali-kazem", "Live From The Field", "Testing homepage carousel rendering.")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("LATEST FROM THE HUNT", response.text)
        self.assertIn("READ ARTICLE", response.text)
        self.assertIn("NEWS &amp; FIELD DISPATCHES", response.text)
        delete_artist_post(post["id"])
        print("[OK] Homepage Hero News Carousel tests passed.")

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

    def test_artist_post_create_and_delete_with_session(self):
        auth_client = TestClient(app)
        auth_client.cookies.set("ubh_admin_session", get_session_token())

        # 1. Create a post
        res_add = auth_client.post("/admin/posts/add", data={
            "artist_slug": "ali-kazem",
            "title": "Temporary Test Transmission",
            "body": "This is a temporary test post to verify creation and deletion flow.",
            "media_url": "/static/assets/image.jpg"
        }, follow_redirects=False)
        self.assertEqual(res_add.status_code, 303)

        # Verify post appears in admin tab
        res_admin = auth_client.get("/admin?tab=posts")
        self.assertIn("Temporary Test Transmission", res_admin.text)
        self.assertIn("🗑️ Delete Post", res_admin.text)

        # 2. Extract post id
        from services.firebase_service import get_all_artist_posts, delete_artist_post
        posts = get_all_artist_posts()
        created = [p for p in posts if p.get("title") == "Temporary Test Transmission"]
        self.assertTrue(len(created) > 0)
        post_id = created[0]["id"]

        # 3. Delete the post via POST /admin/posts/delete
        res_del = auth_client.post("/admin/posts/delete", data={
            "post_id": post_id
        }, follow_redirects=False)
        self.assertEqual(res_del.status_code, 303)

        # Verify post is removed
        posts_after = get_all_artist_posts()
        self.assertFalse(any(p.get("id") == post_id for p in posts_after))
        print("[OK] Artist post creation and deletion with session cookie passed.")

    def test_email_subscription_api(self):
        response = self.client.post("/subscribe", data={"email": "newfan@ubh.com"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        print("[OK] Email subscription API test passed.")

if __name__ == "__main__":
    unittest.main()
