import unittest
from starlette.testclient import TestClient
from main import app
from services.stripe_service import create_checkout_session
from unittest.mock import patch, MagicMock

class TestFooterAndStripe(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_footer_and_admin_security(self):
        # 1. Verify Homepage Footer
        r_home = self.client.get("/")
        self.assertEqual(r_home.status_code, 200)
        self.assertNotIn("ENTER ADMIN CMS", r_home.text)
        self.assertIn("UNICORN BOUNTY HUNTERS", r_home.text)

        # 2. Verify /admin login page
        r_admin = self.client.get("/admin")
        self.assertEqual(r_admin.status_code, 200)
        self.assertIn("UBH CMS PORTAL", r_admin.text)

        # 3. Verify authenticated admin login
        r_login = self.client.post("/admin/login", data={"key": "shadowurameshi2026"}, follow_redirects=True)
        self.assertEqual(r_login.status_code, 200)
        self.assertIn("ADMIN CMS ENGINE", r_login.text)

    def test_live_stripe_session(self):
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/c/pay/cs_live_sample12345"
        mock_session.id = "cs_live_sample12345"

        with patch("services.stripe_service.STRIPE_SECRET_KEY", "sk_live_testkey12345"):
            with patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create:
                live_res = create_checkout_session(
                    slot_id="2026-12-01-slot-1",
                    artist_name="Live Artist",
                    artist_email="artist@live.com",
                    package_type="studio"
                )
                mock_create.assert_called_once()
                self.assertEqual(live_res["url"], "https://checkout.stripe.com/c/pay/cs_live_sample12345")
                self.assertFalse(live_res.get("is_mock", False))

if __name__ == "__main__":
    unittest.main()
