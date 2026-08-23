"""Verification script for hidden public admin link, direct admin access, and live stripe redirect logic."""
import http.client
import urllib.parse
import sys

def request(method, path, data=None, headers=None):
    conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
    req_headers = headers or {}
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data)
        req_headers["Content-Type"] = "application/x-www-form-urlencoded"
    
    conn.request(method, path, body=body, headers=req_headers)
    resp = conn.getresponse()
    resp_body = resp.read().decode("utf-8", errors="replace")
    resp_headers = dict(resp.getheaders())
    conn.close()
    return {
        "status": resp.status,
        "headers": resp_headers,
        "location": resp_headers.get("location", resp_headers.get("Location", "")),
        "body": resp_body
    }

print("=" * 65, flush=True)
print("FOOTER ADMIN REMOVAL & LIVE STRIPE VERIFICATION", flush=True)
print("=" * 65, flush=True)

checks = []

# 1. Verify Homepage Footer has no Admin link
r_home = request("GET", "/")
checks.append(("GET / Footer: No 'ENTER ADMIN CMS'", "ENTER ADMIN CMS" not in r_home["body"]))
checks.append(("GET / Footer: No 'PORTAL' section", "PORTAL" not in r_home["body"]))
checks.append(("GET / Footer: Brand info intact", "UNICORN BOUNTY HUNTERS" in r_home["body"]))
checks.append(("GET / Footer: Quick links intact", "Studio Recording &amp; Rates" in r_home["body"] or "Studio Recording" in r_home["body"]))
checks.append(("GET / Footer: Council links intact", "Ali Kazem" in r_home["body"]))

# 2. Verify /services Footer has no Admin link
r_serv = request("GET", "/services")
checks.append(("GET /services Footer: No 'ENTER ADMIN CMS'", "ENTER ADMIN CMS" not in r_serv["body"]))

# 3. Verify /admin remains fully accessible directly
r_admin_login = request("GET", "/admin")
checks.append(("GET /admin: Login prompt accessible (200 OK)", r_admin_login["status"] == 200 and "UBH CMS PORTAL" in r_admin_login["body"]))

r_admin_auth = request("GET", "/admin?key=[REDACTED_ADMIN_SECRET]")
checks.append(("GET /admin?key=...: Authenticated CMS dashboard accessible (200 OK)", r_admin_auth["status"] == 200 and "ADMIN CMS ENGINE" in r_admin_auth["body"]))

# 4. Verify live Stripe redirect logic unit check
from services.stripe_service import create_checkout_session
from unittest.mock import patch, MagicMock

# Simulate a live Stripe checkout session
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
        checks.append(("Live Stripe Key: Bypasses mock and generates checkout.stripe.com URL", live_res["url"] == "https://checkout.stripe.com/c/pay/cs_live_sample12345" and not live_res.get("is_mock", False)))

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
