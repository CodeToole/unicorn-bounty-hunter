"""Verification script for hidden public admin link, direct admin access, and live stripe redirect logic (In-Memory)."""
import sys
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token
from services.stripe_service import create_checkout_session

client = TestClient(app)

print("=" * 65, flush=True)
print("FOOTER ADMIN REMOVAL & LIVE STRIPE VERIFICATION (IN-MEMORY)", flush=True)
print("=" * 65, flush=True)

checks = []

# 1. Verify Homepage Footer has no Admin link
r_home = client.get("/")
checks.append(("GET / Footer: No 'ENTER ADMIN CMS'", "ENTER ADMIN CMS" not in r_home.text))
checks.append(("GET / Footer: No 'PORTAL' section", "PORTAL" not in r_home.text))
checks.append(("GET / Footer: Brand info intact", "UNICORN BOUNTY HUNTERS" in r_home.text))
checks.append(("GET / Footer: Quick links intact", "Studio Recording &amp; Rates" in r_home.text or "Studio Recording" in r_home.text))
checks.append(("GET / Footer: Council links intact", "Ali Kazem" in r_home.text))

# 2. Verify /services Footer has no Admin link
r_serv = client.get("/services")
checks.append(("GET /services Footer: No 'ENTER ADMIN CMS'", "ENTER ADMIN CMS" not in r_serv.text))

# 3. Verify /admin login prompt accessible directly
r_admin_login = client.get("/admin")
checks.append(("GET /admin: Login prompt accessible (200 OK)", r_admin_login.status_code == 200 and "UBH CMS PORTAL" in r_admin_login.text))

# 4. Verify authenticated CMS dashboard with session cookie
client_auth = TestClient(app)
client_auth.cookies.set("ubh_admin_session", get_session_token())
r_admin_auth = client_auth.get("/admin")
checks.append(("GET /admin (cookie auth): Authenticated CMS dashboard accessible (200 OK)", r_admin_auth.status_code == 200 and "ADMIN CMS ENGINE" in r_admin_auth.text))

# 5. Verify live Stripe redirect logic unit check
mock_session = MagicMock()
mock_session.url = "https://checkout.stripe.com/c/pay/cs_live_sample12345"
mock_session.id = "cs_live_sample12345"

with patch("services.stripe_service.STRIPE_SECRET_KEY", "sk_live_testkey12345"), \
     patch("services.stripe_service.is_live_stripe_enabled", return_value=True), \
     patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create:
    live_res = create_checkout_session(
        slot_id="2026-12-01-slot-1",
        artist_name="Live Artist",
        artist_email="artist@live.com",
        package_type="studio"
    )
    mock_create.assert_called_once()
    checks.append(("Live Stripe Key: Bypasses mock and generates checkout.stripe.com URL", live_res.get("url") == "https://checkout.stripe.com/c/pay/cs_live_sample12345" and not live_res.get("is_mock", False)))

all_pass = True
for label, passed in checks:
    tag = "OK" if passed else "FAIL"
    if not passed:
        all_pass = False
    print(f"  {tag:4}  {label}", flush=True)

print("=" * 65, flush=True)
if all_pass:
    print("RESULT: ALL FOOTER & LIVE STRIPE CHECKS PASSED (100% SUCCESS)", flush=True)
else:
    print("RESULT: SOME CHECKS FAILED", flush=True)
print("=" * 65, flush=True)

sys.exit(0 if all_pass else 1)
