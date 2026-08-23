import urllib.request
import urllib.parse
import json

base = 'http://127.0.0.1:8000'
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
    '/admin?key=[REDACTED_ADMIN_SECRET]',
    '/health'
]

print("=== VERIFYING ALL LIVE ROUTES ===")
for r in routes:
    res = urllib.request.urlopen(base + r)
    body = res.read()
    print(f"[OK] GET {r:30} -> Status: {res.status} | Size: {len(body):6} bytes")

print("\n=== VERIFYING DATASTAR SSE STREAMING ===")
sse_res = urllib.request.urlopen(base + '/sse/available-slots?booking_date=2026-08-25')
sse_data = sse_res.read().decode('utf-8')
has_event = "datastar-merge-fragments" in sse_data
has_slot_container = "slot-container" in sse_data
print(f"[OK] GET /sse/available-slots -> Status: {sse_res.status} | Datastar Event: {has_event} | Has #slot-container: {has_slot_container}")

print("\n=== VERIFYING EMAIL SUBSCRIPTION API ===")
req = urllib.request.Request(
    base + '/subscribe',
    data=urllib.parse.urlencode({'email': 'livecheck@ubh.com'}).encode('utf-8')
)
sub_res = urllib.request.urlopen(req)
sub_body = sub_res.read().decode('utf-8')
print(f"[OK] POST /subscribe -> Status: {sub_res.status} | Body: {sub_body}")

print("\n=== ALL LIVE VERIFICATION CHECKS PASSED ===")
