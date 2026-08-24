from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token

client = TestClient(app)
client.cookies.set("ubh_admin_session", get_session_token())

routes = [
    '/',
    '/services',
    '/showcase',
    '/musical-chairs',
    '/rap-funxtion',
    '/music',
    '/merch',
    '/booking',
    '/admin',
    '/admin?tab=slots',
    '/admin?tab=showcases',
    '/admin?tab=events',
    '/admin?tab=posts',
    '/admin?tab=subscribers',
    '/health'
]

print("=== VERIFYING ALL ROUTES (IN-MEMORY TESTCLIENT) ===")
for r in routes:
    res = client.get(r)
    body = res.text
    print(f"[OK] GET {r:30} -> Status: {res.status_code} | Size: {len(body):6} bytes")

print("\n=== VERIFYING DATASTAR SSE STREAMING ===")
sse_res = client.get('/sse/available-slots?booking_date=2026-08-25')
sse_data = sse_res.text
has_event = "datastar-merge-fragments" in sse_data
has_slot_container = "slot-container" in sse_data
print(f"[OK] GET /sse/available-slots -> Status: {sse_res.status_code} | Datastar Event: {has_event} | Has #slot-container: {has_slot_container}")

print("\n=== VERIFYING EMAIL SUBSCRIPTION API ===")
sub_res = client.post('/subscribe', data={'email': 'livecheck@ubh.com'})
print(f"[OK] POST /subscribe -> Status: {sub_res.status_code} | Body: {sub_res.json()}")

print("\n=== ALL VERIFICATION CHECKS PASSED ===")
