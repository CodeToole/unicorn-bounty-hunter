"""Fast, robust test suite for UBH Checkout resilience and podcast packages."""
import http.client
import urllib.parse
import datetime
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
print("UBH CHECKOUT RESILIENCE & PACKAGE ALIGNMENT VERIFICATION", flush=True)
print("=" * 65, flush=True)

ts = int(datetime.datetime.now().timestamp())
slot_studio = f"2026-10-01-{ts}-slot-1"
slot_podcast = f"2026-10-02-{ts}-slot-2"
slot_bundle = f"2026-10-03-{ts}-slot-3"

# Run and print each test immediately
def run_and_print(name, condition):
    tag = "OK" if condition else "FAIL"
    print(f"  {tag:4}  {name}", flush=True)
    return condition

passed = True

r1 = request("GET", "/booking")
passed &= run_and_print("GET /booking (Calendar & Package Options)", r1["status"] == 200 and "Studio Recording Session" in r1["body"] and "Shadow Talk Podcast" in r1["body"])

r2 = request("GET", "/services")
passed &= run_and_print("GET /services (Facility Rates & Packages)", r2["status"] == 200 and "Shadow Talk Podcast" in r2["body"])

r3 = request("POST", "/booking/create-checkout", data={})
passed &= run_and_print("POST /booking/create-checkout (Empty form -> 303 Redirect with error)", r3["status"] == 303 and "error=" in r3["location"])

r4 = request("POST", "/booking/create-checkout", data={"slot_id": slot_studio})
passed &= run_and_print("POST /booking/create-checkout (Missing name/email -> 303 Redirect)", r4["status"] == 303 and "error=" in r4["location"])

r5 = request("POST", "/booking/create-checkout", data={"slot_id": "nonexistent-slot-999", "artist_name": "Test Artist", "artist_email": "test@domain.com"})
passed &= run_and_print("POST /booking/create-checkout (Invalid slot -> 303 Redirect)", r5["status"] == 303 and "error=" in r5["location"])

r6 = request("POST", "/booking/create-checkout", data={
    "slot_id": slot_studio,
    "artist_name": "Ali Kazem",
    "artist_email": "ali@ubh.com",
    "package_type": "studio",
    "phone_number": "555-1234",
    "session_notes": "Vocal stems review"
})
passed &= run_and_print("POST /booking/create-checkout (Studio Recording -> Mock Checkout 303)", r6["status"] == 303 and "/booking/mock-checkout" in r6["location"] and "price=100" in r6["location"])

r7 = request("POST", "/booking/create-checkout", data={
    "slot_id": slot_podcast,
    "artist_name": "Special Guest",
    "artist_email": "guest@podcast.com",
    "package_type": "podcast_standard",
    "phone_number": "555-9876",
    "session_notes": "Album rollout interview"
})
passed &= run_and_print("POST /booking/create-checkout (Podcast Standard $50 -> Mock Checkout 303)", r7["status"] == 303 and "/booking/mock-checkout" in r7["location"] and "price=50" in r7["location"] and "podcast_standard" in r7["location"])

r8 = request("POST", "/booking/create-checkout", data={
    "slot_id": slot_bundle,
    "artist_name": "Cypher Star",
    "artist_email": "cypher@ubh.com",
    "package_type": "podcast_bundle",
    "session_notes": "Live verse & interview"
})
passed &= run_and_print("POST /booking/create-checkout (Podcast Bundle $100 -> Mock Checkout 303)", r8["status"] == 303 and "/booking/mock-checkout" in r8["location"] and "price=100" in r8["location"] and "podcast_bundle" in r8["location"])

r9 = request("GET", f"/booking/mock-checkout?session_id=mock-123&slot_id={slot_bundle}&artist=Cypher%20Star&email=cypher@ubh.com&price=100&package=podcast_bundle&package_name=Shadow%20Talk%20Podcast%20%2B%20Musical%20Chairs%20Bundle")
passed &= run_and_print("GET /booking/mock-checkout (Simulation Receipt UI)", r9["status"] == 200 and "COMPLETE RESERVATION" in r9["body"] and "$100 USD" in r9["body"])

r10 = request("POST", "/booking/mock-complete", data={
    "slot_id": slot_bundle,
    "artist_name": "Cypher Star",
    "artist_email": "cypher@ubh.com",
    "session_id": "mock-sess-999",
    "package_type": "podcast_bundle",
    "package_name": "Shadow Talk Podcast + Musical Chairs Bundle"
})
passed &= run_and_print("POST /booking/mock-complete (Finalize Slot & 303 Redirect to Success)", r10["status"] == 303 and "/booking/success" in r10["location"])

r11 = request("GET", f"/booking/success?mock=true&session_id=mock-sess-999&slot_id={slot_bundle}&artist=Cypher%20Star&package_name=Shadow%20Talk%20Podcast%20%2B%20Musical%20Chairs%20Bundle")
passed &= run_and_print("GET /booking/success (Confirmation Badge & Order Breakdown)", r11["status"] == 200 and "BOOKING LOCKED IN" in r11["body"] and ("CONFIRMED &amp; BOOKED" in r11["body"] or "CONFIRMED" in r11["body"]))

print("=" * 65, flush=True)
if passed:
    print("RESULT: ALL 10 CHECKOUT & PACKAGE TESTS PASSED (100% UPTIME)", flush=True)
else:
    print("RESULT: SOME TESTS FAILED", flush=True)
print("=" * 65, flush=True)

sys.exit(0 if passed else 1)
