"""Comprehensive verification of Rap Funxtion Coming Soon status and Admin Event Deletion (In-Memory)."""
import re
import sys
from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token

client = TestClient(app)
client.cookies.set("ubh_admin_session", get_session_token())

print("=" * 65, flush=True)
print("RAP FUNXTION COMING SOON & ADMIN EVENT DELETION TEST SUITE (IN-MEMORY)", flush=True)
print("=" * 65, flush=True)

checks = []

# 1. Verify /rap-funxtion displays COMING SOON
r_rf = client.get("/rap-funxtion")
checks.append(("GET /rap-funxtion: Returns 200 OK", r_rf.status_code == 200))
checks.append(("GET /rap-funxtion: Displays 'STATUS: COMING SOON'", "STATUS: COMING SOON" in r_rf.text))
checks.append(("GET /rap-funxtion: Displays new finalized announcement copy", "lineup configurations are currently being finalized" in r_rf.text))
checks.append(("GET /rap-funxtion: Does NOT contain 'RESCHEDULING IN PROGRESS'", "RESCHEDULING IN PROGRESS" not in r_rf.text))

# 2. Verify Admin Events Tab
r_admin_events = client.get("/admin?tab=events")
checks.append(("GET /admin events tab: Returns 200 OK", r_admin_events.status_code == 200))
checks.append(("GET /admin events tab: Displays 'Rap Funxtion' event", "Rap Funxtion" in r_admin_events.text))
checks.append(("GET /admin events tab: Delete Event button present", "Delete Event" in r_admin_events.text and "/admin/events/delete" in r_admin_events.text))

# 3. Add a temporary event to test creation and deletion
r_add = client.post("/admin/events/add", data={
    "title": "Rap Funxtion 17 Winter Showcase",
    "date": "December 2026",
    "status": "Tickets Live",
    "flyer_url": "/static/assets/rf16_flyer_new.jpg",
    "ticket_url": "https://tickets.example.com",
    "description": "Exclusive winter headline showcase featuring full roster."
}, follow_redirects=False)
checks.append(("POST /admin/events/add: 303 Redirect to admin", r_add.status_code == 303 and "tab=events" in r_add.headers.get("location", "")))

# 4. Verify public /rap-funxtion reflects new live event
r_rf_new = client.get("/rap-funxtion")
checks.append(("GET /rap-funxtion: Displays newly added event title", "RAP FUNXTION 17 WINTER SHOWCASE" in r_rf_new.text))
checks.append(("GET /rap-funxtion: Displays 'STATUS: TICKETS LIVE'", "STATUS: TICKETS LIVE" in r_rf_new.text))

# 5. Extract event ID from admin events list and delete it
r_admin_list = client.get("/admin?tab=events")
match = re.search(r'name="event_id"\s+value="([^"]+)"', r_admin_list.text)
event_id_to_delete = match.group(1) if match else None

if event_id_to_delete:
    r_delete = client.post("/admin/events/delete", data={
        "event_id": event_id_to_delete
    }, follow_redirects=False)
    checks.append(("POST /admin/events/delete: 303 Redirect after delete", r_delete.status_code == 303 and "Event+deleted" in r_delete.headers.get("location", "")))
else:
    checks.append(("POST /admin/events/delete: Extract event ID for deletion", False))

# 6. Verify /rap-funxtion reverted back to COMING SOON
r_rf_final = client.get("/rap-funxtion")
checks.append(("GET /rap-funxtion after delete: Reverts to 'STATUS: COMING SOON'", "STATUS: COMING SOON" in r_rf_final.text))

all_passed = True
for label, passed in checks:
    tag = "OK" if passed else "FAIL"
    if not passed:
        all_passed = False
    print(f"  {tag:4}  {label}", flush=True)

print("=" * 65, flush=True)
if all_passed:
    print("RESULT: ALL 11 RAP FUNXTION & EVENT CHECKS PASSED (100% SUCCESS)", flush=True)
else:
    print("RESULT: SOME CHECKS FAILED", flush=True)
print("=" * 65, flush=True)

sys.exit(0 if all_passed else 1)
