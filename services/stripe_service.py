import stripe
from typing import Dict, Any, Optional
from config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, DOMAIN_URL
from services.firebase_service import get_slot_by_id, update_slot_status

stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(
    slot_id: str,
    artist_name: str,
    artist_email: str,
    phone_number: str = "",
    package_type: str = "studio",
    session_notes: str = ""
) -> Dict[str, Any]:
    slot = get_slot_by_id(slot_id)
    if not slot or slot.get("status") != "available":
        return {"error": "Selected slot is no longer available. Please choose another date or time."}

    time_label = slot.get("time_label", "2 Hours")
    date_str = slot.get("date", "")

    # Determine product details based on package_type
    if package_type == "podcast_standard":
        price_usd = 50.0
        package_name = "Shadow Talk Podcast — Standard Episode (1 Hr)"
        package_desc = f"Date: {date_str} | Time: {time_label} | Host/Guest: {artist_name}"
    elif package_type == "podcast_bundle":
        price_usd = 100.0
        package_name = "Shadow Talk Podcast + Musical Chairs Cypher Bundle"
        package_desc = f"Date: {date_str} | Time: {time_label} | Artist: {artist_name} (Includes Cypher Feature)"
    else:
        # Default studio recording
        package_type = "studio"
        price_usd = float(slot.get("price", 100))
        package_name = f"UBH Studio Recording Session — {time_label}"
        package_desc = f"Date: {date_str} | Time: {time_label} | Artist: {artist_name}"

    # Check if we have a real Stripe API key (not mock)
    active_key = STRIPE_SECRET_KEY
    if active_key and not active_key.startswith("sk_test_mock") and not active_key.startswith("placeholder"):
        try:
            stripe.api_key = active_key
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=artist_email,
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": package_name,
                            "description": package_desc,
                        },
                        "unit_amount": int(price_usd * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"{DOMAIN_URL}/booking/success?session_id={{CHECKOUT_SESSION_ID}}&slot_id={slot_id}&artist={artist_name}&package={package_type}",
                cancel_url=f"{DOMAIN_URL}/booking?cancelled=true",
                metadata={
                    "slot_id": slot_id,
                    "artist_name": artist_name,
                    "artist_email": artist_email,
                    "phone_number": phone_number,
                    "package_type": package_type,
                    "package_name": package_name,
                    "date": date_str,
                    "time_label": time_label,
                    "session_notes": session_notes
                }
            )
            return {"url": session.url, "id": session.id, "is_mock": False, "price": price_usd, "package_name": package_name}
        except Exception as e:
            print(f"Stripe API error: {e}. Generating simulated checkout link for local testing.")

    # Simulated Mock Checkout for local testing
    mock_session_id = f"cs_test_mock_{slot_id}_{int(price_usd)}"
    import urllib.parse
    encoded_pkg_name = urllib.parse.quote(package_name)
    encoded_artist = urllib.parse.quote(artist_name)
    encoded_email = urllib.parse.quote(artist_email)
    mock_url = f"{DOMAIN_URL}/booking/mock-checkout?session_id={mock_session_id}&slot_id={slot_id}&artist={encoded_artist}&email={encoded_email}&price={int(price_usd)}&package={package_type}&package_name={encoded_pkg_name}"
    return {"url": mock_url, "id": mock_session_id, "is_mock": True, "price": price_usd, "package_name": package_name}

def process_successful_payment(
    slot_id: str,
    artist_name: str,
    artist_email: str,
    package_type: Optional[str] = None,
    package_name: Optional[str] = None
) -> bool:
    return update_slot_status(
        slot_id=slot_id,
        status="booked",
        artist_name=artist_name,
        artist_email=artist_email,
        package_type=package_type,
        package_name=package_name
    )

def verify_webhook_event(payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
    if STRIPE_WEBHOOK_SECRET and not STRIPE_WEBHOOK_SECRET.startswith("whsec_mock") and not STRIPE_WEBHOOK_SECRET.startswith("placeholder"):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
            return event
        except Exception as e:
            print(f"Webhook verification error: {e}")
            return None
    # In mock / dev mode, attempt parsing json
    try:
        import json
        return json.loads(payload.decode("utf-8"))
    except Exception:
        return None
