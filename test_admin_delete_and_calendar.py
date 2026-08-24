"""Comprehensive in-memory test script verifying Admin Booking Deletion and Date Dropdown alignment."""
from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token
from services.firebase_service import get_slot_by_id, update_slot_status
import sys

client = TestClient(app)
client.cookies.set("ubh_admin_session", get_session_token())

print("=" * 65, flush=True)
print("ADMIN BOOKING DELETION & DATE DROPDOWN VERIFICATION (IN-MEMORY)", flush=True)
print("=" * 65, flush=True)

test_date = "2026-12-25"
slot_id = f"{test_date}-slot-1"

checks = []

# 1. Verify Date Selector dropdown & SSE trigger in /booking
r_book = client.get("/booking")
checks.append(("GET /booking: Dropdown select element present", '<select' in r_book.text and 'id="booking-date-select"' in r_book.text))
checks.append(("GET /booking: Datastar on_change SSE trigger attached", 'data-on-change="$$get(\'/sse/available-slots' in r_book.text))
checks.append(("GET /booking: Custom date picker available", 'type="date"' in r_book.text))

# 2. Verify SSE available slots endpoint
r_sse = client.get(f"/sse/available-slots?booking_date={test_date}")
checks.append(("GET /sse/available-slots: SSE stream returned (200 OK)", r_sse.status_code == 200 and "datastar-merge-fragments" in r_sse.text))

# 3. Simulate customer booking slot
update_slot_status(
    slot_id=slot_id,
    status="booked",
    artist_name="VIP Rapper",
    artist_email="vip@music.com",
    package_type="podcast_bundle",
    package_name="Podcast + Musical Chairs Bundle"
)
slot_data = get_slot_by_id(slot_id)
checks.append(("Slot booked in server store", slot_data.get("status") == "booked" and slot_data.get("artist_name") == "VIP Rapper"))

# 4. View Admin Studio Slots Tab and check for Booked Details & Delete Button
r_admin_slots = client.get(f"/admin?tab=slots&date={test_date}")
checks.append(("GET /admin slots tab: Displays booked customer info", "VIP Rapper" in r_admin_slots.text and "vip@music.com" in r_admin_slots.text))
checks.append(("GET /admin slots tab: Delete / Clear Booking button rendered", "Clear / Delete Booking" in r_admin_slots.text and "/admin/slots/delete" in r_admin_slots.text))

# 5. Execute Delete / Clear Booking via POST /admin/slots/delete
r_delete = client.post("/admin/slots/delete", data={
    "slot_id": slot_id,
    "date": test_date
}, follow_redirects=False)
checks.append(("POST /admin/slots/delete: 303 Redirect to admin", r_delete.status_code == 303 and "tab=slots" in r_delete.headers.get("location", "")))

# 6. Check admin UI after deletion: Slot is back to AVAILABLE and customer info is gone
r_admin_after = client.get(f"/admin?tab=slots&date={test_date}")
checks.append(("GET /admin slots after delete: Shows AVAILABLE", "AVAILABLE" in r_admin_after.text))
checks.append(("GET /admin slots after delete: Customer details removed", "VIP Rapper" not in r_admin_after.text))

# 7. Check public booking widget: Slot is open for booking again!
r_public_after = client.get(f"/sse/available-slots?booking_date={test_date}")
checks.append(("GET /sse/available-slots after delete: Slot re-opened for public booking", slot_id in r_public_after.text))

all_passed = True
for label, passed in checks:
    tag = "OK" if passed else "FAIL"
    if not passed:
        all_passed = False
    print(f"  {tag:4}  {label}", flush=True)

print("=" * 65, flush=True)
if all_passed:
    print("RESULT: ALL DELETION & CALENDAR CHECKS PASSED (100% SUCCESS)", flush=True)
else:
    print("RESULT: SOME CHECKS FAILED", flush=True)
print("=" * 65, flush=True)

sys.exit(0 if all_passed else 1)
