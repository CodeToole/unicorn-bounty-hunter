import unittest
from starlette.testclient import TestClient
from main import app
from config import ADMIN_SECRET_KEY
from services.firebase_service import create_user_account, authenticate_user_account, get_all_user_accounts

class TestAdminUserCreate(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app, follow_redirects=False)

    def test_post_admin_user_create_unauthenticated(self):
        """Unauthenticated requests should be rejected with an error redirect."""
        res = self.client.post("/admin/users/create", data={
            "email": "newuser@ubh.com",
            "password": "securepassword123",
            "role": "artist_admin",
            "artist_slug": "malik-rose"
        })
        self.assertEqual(res.status_code, 303)
        self.assertIn("/admin?error=Unauthorized", res.headers.get("location", ""))

    def test_post_admin_user_create_as_artist_admin(self):
        """Artist Admin (non-super admin) attempts to create a user account -> Blocked with error redirect."""
        create_user_account("artist_user@ubh.com", "pass123", role="artist_admin", artist_slug="malik-rose")
        self.client.post("/admin/login", data={
            "email": "artist_user@ubh.com",
            "password": "pass123"
        })

        res = self.client.post("/admin/users/create", data={
            "email": "another@ubh.com",
            "password": "securepassword123",
            "role": "artist_admin",
            "artist_slug": "ali-kazem"
        })
        self.assertEqual(res.status_code, 303)
        self.assertIn("/admin?error=Unauthorized", res.headers.get("location", ""))

    def test_post_admin_user_create_missing_fields_as_super_admin(self):
        """Super Admin submits creation form missing required email or password -> Error redirect."""
        self.client.post("/admin/login", data={"key": ADMIN_SECRET_KEY})

        # Missing password
        res_no_pw = self.client.post("/admin/users/create", data={
            "email": "incomplete@ubh.com",
            "password": "",
            "role": "artist_admin",
            "artist_slug": "malik-rose"
        })
        self.assertEqual(res_no_pw.status_code, 303)
        self.assertIn("error=Email+and+password+are+required", res_no_pw.headers.get("location", ""))

        # Missing email
        res_no_email = self.client.post("/admin/users/create", data={
            "email": "   ",
            "password": "password123",
            "role": "artist_admin",
            "artist_slug": "malik-rose"
        })
        self.assertEqual(res_no_email.status_code, 303)
        self.assertIn("error=Email+and+password+are+required", res_no_email.headers.get("location", ""))

    def test_post_admin_user_create_success_as_super_admin(self):
        """Super Admin creates new artist_admin and super_admin accounts successfully."""
        self.client.post("/admin/login", data={"key": ADMIN_SECRET_KEY})

        # 1. Create Artist Admin
        res_artist = self.client.post("/admin/users/create", data={
            "email": "new_artist@ubh.com",
            "password": "ArtistPassword123!",
            "role": "artist_admin",
            "artist_slug": "unkn0wn"
        })
        self.assertEqual(res_artist.status_code, 303)
        self.assertIn("tab=users", res_artist.headers.get("location", ""))
        self.assertIn("new_artist@ubh.com", res_artist.headers.get("location", ""))

        auth_user = authenticate_user_account("new_artist@ubh.com", "ArtistPassword123!")
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user["email"], "new_artist@ubh.com")
        self.assertEqual(auth_user["role"], "artist_admin")
        self.assertEqual(auth_user["artist_slug"], "unkn0wn")

        # 2. Create Super Admin
        res_admin = self.client.post("/admin/users/create", data={
            "email": "new_superadmin@ubh.com",
            "password": "SuperPassword123!",
            "role": "super_admin",
            "artist_slug": ""
        })
        self.assertEqual(res_admin.status_code, 303)
        self.assertIn("tab=users", res_admin.headers.get("location", ""))
        self.assertIn("new_superadmin@ubh.com", res_admin.headers.get("location", ""))

        auth_super = authenticate_user_account("new_superadmin@ubh.com", "SuperPassword123!")
        self.assertIsNotNone(auth_super)
        self.assertEqual(auth_super["role"], "super_admin")

        # Verify listed in all accounts
        all_users = get_all_user_accounts()
        emails = [u["email"] for u in all_users]
        self.assertIn("new_artist@ubh.com", emails)
        self.assertIn("new_superadmin@ubh.com", emails)

if __name__ == "__main__":
    unittest.main()
