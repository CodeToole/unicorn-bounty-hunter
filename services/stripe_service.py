import stripe
import json
from typing import Dict, Any, Optional
from config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    DOMAIN_URL,
    IS_PRODUCTION,
    is_live_stripe_enabled,
    is_mock_payment_allowed
)
from services.firebase_service import get_slot_by_id, update_slot_status

if STRIPE_SECRET_KEY:
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

    # Check if we have a real / live Stripe API key
    if is_live_stripe_enabled():
        try:
            stripe.api_key = STRIPE_SECRET_KEY
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
            print(f"Stripe API error: {e}")
            return {"error": f"Stripe Checkout error: {str(e)}"}

    # If mock payments are strictly prohibited (e.g. production), reject
    if not is_mock_payment_allowed():
        return {"error": "Mock checkout is disabled in this environment."}

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
    """
    Verifies incoming Stripe webhook events.
    In production mode, strictly enforces HMAC signature verification with construct_event.
    """
    if IS_PRODUCTION:
        if not STRIPE_WEBHOOK_SECRET or not sig_header or STRIPE_WEBHOOK_SECRET.startswith("whsec_mock") or STRIPE_WEBHOOK_SECRET.startswith("placeholder"):
            print("Webhook Error: STRIPE_WEBHOOK_SECRET must be configured in production.")
            return None
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            print(f"Production webhook signature verification error: {e}")
            return None

    # In development mode, verify signature if secret provided, or fallback to json parse in test simulator
    if STRIPE_WEBHOOK_SECRET and not STRIPE_WEBHOOK_SECRET.startswith("whsec_mock") and not STRIPE_WEBHOOK_SECRET.startswith("placeholder"):
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            print(f"Webhook verification error: {e}")
            return None

    # Fallback for dev / mock testing
    try:
        return json.loads(payload.decode("utf-8"))
    except Exception:
        return None
