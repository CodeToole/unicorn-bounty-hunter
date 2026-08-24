"""Fast, robust test suite for UBH Checkout resilience and podcast packages (In-Memory)."""
import datetime
import sys
from unittest.mock import patch
from starlette.testclient import TestClient
from main import app
from services.firebase_service import get_slot_by_id, update_slot_status

client = TestClient(app)

print("=" * 65, flush=True)
print("UBH CHECKOUT RESILIENCE & PACKAGE ALIGNMENT VERIFICATION (IN-MEMORY)", flush=True)
print("=" * 65, flush=True)

ts = int(datetime.datetime.now().timestamp())
slot_studio = f"2026-10-01-{ts}-slot-1"
slot_podcast = f"2026-10-02-{ts}-slot-2"
slot_bundle = f"2026-10-03-{ts}-slot-3"

def run_and_print(name, condition):
    tag = "OK" if condition else "FAIL"
    print(f"  {tag:4}  {name}", flush=True)
    return condition

passed = True

r1 = client.get("/booking")
passed &= run_and_print("GET /booking (Calendar & Package Options)", r1.status_code == 200 and "Studio Recording Session" in r1.text and "Shadow Talk Podcast" in r1.text)

r2 = client.get("/services")
passed &= run_and_print("GET /services (Facility Rates & Packages)", r2.status_code == 200 and "Shadow Talk Podcast" in r2.text)

r3 = client.post("/booking/create-checkout", data={}, follow_redirects=False)
passed &= run_and_print("POST /booking/create-checkout (Empty form -> 303 Redirect with error)", r3.status_code == 303 and "error=" in r3.headers.get("location", ""))

r4 = client.post("/booking/create-checkout", data={"slot_id": slot_studio}, follow_redirects=False)
passed &= run_and_print("POST /booking/create-checkout (Missing name/email -> 303 Redirect)", r4.status_code == 303 and "error=" in r4.headers.get("location", ""))

r5 = client.post("/booking/create-checkout", data={"slot_id": "nonexistent-slot-999", "artist_name": "Test Artist", "artist_email": "test@domain.com"}, follow_redirects=False)
passed &= run_and_print("POST /booking/create-checkout (Invalid slot -> 303 Redirect)", r5.status_code == 303 and "error=" in r5.headers.get("location", ""))

with patch("config.STRIPE_SECRET_KEY", "sk_test_mock_key"), \
     patch("services.stripe_service.STRIPE_SECRET_KEY", "sk_test_mock_key"), \
     patch("services.stripe_service.is_mock_payment_allowed", return_value=True), \
     patch("routes.booking.is_mock_payment_allowed", return_value=True):
    r6 = client.post("/booking/create-checkout", data={
        "slot_id": slot_studio,
        "artist_name": "Ali Kazem",
        "artist_email": "ali@ubh.com",
        "package_type": "studio",
        "phone_number": "555-1234",
        "session_notes": "Vocal stems review"
    }, follow_redirects=False)
    passed &= run_and_print("POST /booking/create-checkout (Studio Recording -> Mock Checkout 303)", r6.status_code == 303 and "/booking/mock-checkout" in r6.headers.get("location", "") and "price=100" in r6.headers.get("location", ""))

    r7 = client.post("/booking/create-checkout", data={
        "slot_id": slot_podcast,
        "artist_name": "Special Guest",
        "artist_email": "guest@podcast.com",
        "package_type": "podcast_standard",
        "phone_number": "555-9876",
        "session_notes": "Album rollout interview"
    }, follow_redirects=False)
    passed &= run_and_print("POST /booking/create-checkout (Podcast Standard $50 -> Mock Checkout 303)", r7.status_code == 303 and "/booking/mock-checkout" in r7.headers.get("location", "") and "price=50" in r7.headers.get("location", "") and "podcast_standard" in r7.headers.get("location", ""))

    r8 = client.post("/booking/create-checkout", data={
        "slot_id": slot_bundle,
        "artist_name": "Cypher Star",
        "artist_email": "cypher@ubh.com",
        "package_type": "podcast_bundle",
        "session_notes": "Live verse & interview"
    }, follow_redirects=False)
    passed &= run_and_print("POST /booking/create-checkout (Podcast Bundle $100 -> Mock Checkout 303)", r8.status_code == 303 and "/booking/mock-checkout" in r8.headers.get("location", "") and "price=100" in r8.headers.get("location", "") and "podcast_bundle" in r8.headers.get("location", ""))

    r9 = client.get(f"/booking/mock-checkout?session_id=mock-123&slot_id={slot_bundle}&artist=Cypher%20Star&email=cypher@ubh.com&price=100&package=podcast_bundle&package_name=Shadow%20Talk%20Podcast%20%2B%20Musical%20Chairs%20Bundle")
    passed &= run_and_print("GET /booking/mock-checkout (Simulation Receipt UI)", r9.status_code == 200 and "COMPLETE RESERVATION" in r9.text and "$100 USD" in r9.text)

    r10 = client.post("/booking/mock-complete", data={
        "slot_id": slot_bundle,
        "artist_name": "Cypher Star",
        "artist_email": "cypher@ubh.com",
        "session_id": "mock-sess-999",
        "package_type": "podcast_bundle",
        "package_name": "Shadow Talk Podcast + Musical Chairs Bundle"
    }, follow_redirects=False)
    passed &= run_and_print("POST /booking/mock-complete (Finalize Slot & 303 Redirect to Success)", r10.status_code == 303 and "/booking/success" in r10.headers.get("location", ""))

r11 = client.get(f"/booking/success?mock=true&session_id=mock-sess-999&slot_id={slot_bundle}&artist=Cypher%20Star&package_name=Shadow%20Talk%20Podcast%20%2B%20Musical%20Chairs%20Bundle")
passed &= run_and_print("GET /booking/success (Confirmation Badge & Order Breakdown)", r11.status_code == 200 and "BOOKING LOCKED IN" in r11.text and ("CONFIRMED &amp; BOOKED" in r11.text or "CONFIRMED" in r11.text))

print("=" * 65, flush=True)
if passed:
    print("RESULT: ALL 10 CHECKOUT & PACKAGE TESTS PASSED (100% UPTIME)", flush=True)
else:
    print("RESULT: SOME TESTS FAILED", flush=True)
print("=" * 65, flush=True)

sys.exit(0 if passed else 1)
