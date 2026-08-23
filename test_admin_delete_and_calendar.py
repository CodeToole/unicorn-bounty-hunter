"""Comprehensive test script verifying Admin Booking Deletion and Date Dropdown alignment via HTTP."""
import http.client
import urllib.parse
import sys

def request(method, path, data=None, headers=None, is_sse=False):
    conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
    req_headers = headers or {}
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data)
        req_headers["Content-Type"] = "application/x-www-form-urlencoded"
    
    conn.request(method, path, body=body, headers=req_headers)
    resp = conn.getresponse()
    if is_sse:
        resp_body = resp.read(8192).decode("utf-8", errors="replace")
    else:
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
print("ADMIN BOOKING DELETION & DATE DROPDOWN VERIFICATION", flush=True)
print("=" * 65, flush=True)

test_date = "2026-12-25"
slot_id = f"{test_date}-slot-1"

checks = []

# 1. Verify Date Selector dropdown & SSE trigger in /booking
r_book = request("GET", "/booking")
checks.append(("GET /booking: Dropdown select element present", '<select' in r_book["body"] and 'id="booking-date-select"' in r_book["body"]))
checks.append(("GET /booking: Datastar on_change SSE trigger attached", 'data-on-change="$$get(\'/sse/available-slots' in r_book["body"]))
checks.append(("GET /booking: Custom date picker available", 'type="date"' in r_book["body"]))

# 2. Verify SSE available slots endpoint
r_sse = request("GET", f"/sse/available-slots?booking_date={test_date}", is_sse=True)
checks.append(("GET /sse/available-slots: SSE stream returned (200 OK)", r_sse["status"] == 200 and "datastar-merge-fragments" in r_sse["body"]))

# 3. Simulate customer booking slot via HTTP checkout simulator
r_create = request("POST", "/booking/create-checkout", data={
    "slot_id": slot_id,
    "artist_name": "VIP Rapper",
    "artist_email": "vip@music.com",
    "package_type": "podcast_bundle",
    "session_notes": "Live freestyle & interview"
})
checks.append(("POST /booking/create-checkout: Slot checkout generated", r_create["status"] == 303))

r_complete = request("POST", "/booking/mock-complete", data={
    "slot_id": slot_id,
    "artist_name": "VIP Rapper",
    "artist_email": "vip@music.com",
    "session_id": "sess-vip-123",
    "package_type": "podcast_bundle",
    "package_name": "Podcast + Musical Chairs Bundle"
})
checks.append(("POST /booking/mock-complete: Slot booked in server store", r_complete["status"] == 303))

# 4. View Admin Studio Slots Tab and check for Booked Details & Delete Button
r_admin_slots = request("GET", f"/admin?key=shadowurameshi2026&tab=slots&date={test_date}")
checks.append(("GET /admin slots tab: Displays booked customer info", "VIP Rapper" in r_admin_slots["body"] and "vip@music.com" in r_admin_slots["body"]))
checks.append(("GET /admin slots tab: Delete / Clear Booking button rendered", "Clear / Delete Booking" in r_admin_slots["body"] and "/admin/slots/delete" in r_admin_slots["body"]))

# 5. Execute Delete / Clear Booking via POST /admin/slots/delete
r_delete = request("POST", "/admin/slots/delete", data={
    "key": "shadowurameshi2026",
    "slot_id": slot_id,
    "date": test_date
})
checks.append(("POST /admin/slots/delete: 303 Redirect to admin", r_delete["status"] == 303 and "tab=slots" in r_delete["location"]))

# 6. Check admin UI after deletion: Slot is back to AVAILABLE and customer info is gone
r_admin_after = request("GET", f"/admin?key=shadowurameshi2026&tab=slots&date={test_date}")
checks.append(("GET /admin slots after delete: Shows AVAILABLE", "AVAILABLE" in r_admin_after["body"]))
checks.append(("GET /admin slots after delete: Customer details removed", "VIP Rapper" not in r_admin_after["body"]))

# 7. Check public booking widget: Slot is open for booking again!
r_public_after = request("GET", f"/sse/available-slots?booking_date={test_date}", is_sse=True)
checks.append(("GET /sse/available-slots after delete: Slot re-opened for public booking", slot_id in r_public_after["body"]))

all_passed = True
for label, passed in checks:
    tag = "OK" if passed else "FAIL"
    if not passed:
        all_passed = False
    print(f"  {tag:4}  {label}", flush=True)

print("=" * 65, flush=True)
if all_passed:
    print("RESULT: ALL 11 DELETION & CALENDAR CHECKS PASSED (100% SUCCESS)", flush=True)
else:
    print("RESULT: SOME CHECKS FAILED", flush=True)
print("=" * 65, flush=True)

sys.exit(0 if all_passed else 1)
