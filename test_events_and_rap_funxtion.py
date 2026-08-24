"""Comprehensive verification of Rap Funxtion Coming Soon status and Admin Event Deletion."""
import http.client
import urllib.parse
import re
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
print("RAP FUNXTION COMING SOON & ADMIN EVENT DELETION TEST SUITE", flush=True)
print("=" * 65, flush=True)

checks = []

# 1. Verify /rap-funxtion displays COMING SOON
r_rf = request("GET", "/rap-funxtion")
checks.append(("GET /rap-funxtion: Returns 200 OK", r_rf["status"] == 200))
checks.append(("GET /rap-funxtion: Displays 'STATUS: COMING SOON'", "STATUS: COMING SOON" in r_rf["body"]))
checks.append(("GET /rap-funxtion: Displays new finalized announcement copy", "lineup configurations are currently being finalized" in r_rf["body"]))
checks.append(("GET /rap-funxtion: Does NOT contain 'RESCHEDULING IN PROGRESS'", "RESCHEDULING IN PROGRESS" not in r_rf["body"]))

# 2. Verify Admin Events Tab
r_admin_events = request("GET", "/admin?key=[REDACTED_ADMIN_SECRET]&tab=events")
checks.append(("GET /admin events tab: Returns 200 OK", r_admin_events["status"] == 200))
checks.append(("GET /admin events tab: Displays 'Rap Funxtion' event", "Rap Funxtion" in r_admin_events["body"]))
checks.append(("GET /admin events tab: Delete Event button present", "Delete Event" in r_admin_events["body"] and "/admin/events/delete" in r_admin_events["body"]))

# 3. Add a temporary event to test creation and deletion
r_add = request("POST", "/admin/events/add", data={
    "key": "[REDACTED_ADMIN_SECRET]",
    "title": "Rap Funxtion 17 Winter Showcase",
    "date": "December 2026",
    "status": "Tickets Live",
    "flyer_url": "/static/assets/rf16_flyer_new.jpg",
    "ticket_url": "https://tickets.example.com",
    "description": "Exclusive winter headline showcase featuring full roster."
})
checks.append(("POST /admin/events/add: 303 Redirect to admin", r_add["status"] == 303 and "tab=events" in r_add["location"]))

# 4. Verify public /rap-funxtion reflects new live event
r_rf_new = request("GET", "/rap-funxtion")
checks.append(("GET /rap-funxtion: Displays newly added event title", "RAP FUNXTION 17 WINTER SHOWCASE" in r_rf_new["body"]))
checks.append(("GET /rap-funxtion: Displays 'STATUS: TICKETS LIVE'", "STATUS: TICKETS LIVE" in r_rf_new["body"]))

# 5. Extract event ID from admin events list and delete it
r_admin_list = request("GET", "/admin?key=[REDACTED_ADMIN_SECRET]&tab=events")
match = re.search(r'name="event_id"\s+value="([^"]+)"', r_admin_list["body"])
event_id_to_delete = match.group(1) if match else None

if event_id_to_delete:
    r_delete = request("POST", "/admin/events/delete", data={
        "key": "[REDACTED_ADMIN_SECRET]",
        "event_id": event_id_to_delete
    })
    checks.append(("POST /admin/events/delete: 303 Redirect after delete", r_delete["status"] == 303 and "Event+deleted" in r_delete["location"]))
else:
    checks.append(("POST /admin/events/delete: Extract event ID for deletion", False))

# 6. Verify /rap-funxtion reverted back to COMING SOON
r_rf_final = request("GET", "/rap-funxtion")
checks.append(("GET /rap-funxtion after delete: Reverts to 'STATUS: COMING SOON'", "STATUS: COMING SOON" in r_rf_final["body"]))

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
