from fasthtml.common import *
from starlette.responses import RedirectResponse, JSONResponse, Response
import urllib.parse
import datetime

from components.base import Layout
from components.calendar import BookingCalendar
from services.firebase_service import get_slots_for_date, get_slot_by_id, update_slot_status
from services.stripe_service import create_checkout_session, process_successful_payment, verify_webhook_event
from config import is_mock_payment_allowed

booking_app = FastHTML()
rt = booking_app.route

# ----------------- Main Studio Booking Portal -----------------
@rt("/booking")
def get_booking(error: str = "", cancelled: str = ""):
    today_str = datetime.date.today().isoformat()
    slots = get_slots_for_date(today_str)

    calendar_view = BookingCalendar(selected_date=today_str, slots=slots)

    content = Div(
        Div(
            # Header
            Div(
                Span("REAL-TIME STUDIO SCHEDULING", cls="text-xs font-heading font-bold tracking-[0.4em] text-[#D4AF37] uppercase block mb-3"),
                H1("BOOK STUDIO TIME", cls="font-heading text-4xl sm:text-6xl font-black tracking-tight text-white uppercase mb-4"),
                P("Lock in tracking, podcast recording, or mix engineering blocks directly on our official studio calendar.", cls="text-neutral-400 text-sm md:text-base max-w-xl mx-auto leading-relaxed"),
                cls="text-center mb-10"
            ),
            # Alert Banners
            Div(
                P(f"⚠️ {error}", cls="text-rose-400 text-xs font-bold text-center"),
                cls="max-w-2xl mx-auto mb-6 p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl"
            ) if error else None,
            Div(
                P("Checkout cancelled. Your time slot remains temporarily available.", cls="text-amber-400 text-xs font-bold text-center"),
                cls="max-w-2xl mx-auto mb-6 p-3 bg-amber-950/40 border border-amber-800/60 rounded-xl"
            ) if cancelled else None,
            # Interactive Calendar Card
            calendar_view,
            cls="max-w-5xl mx-auto px-6 py-12 md:py-16"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Book Studio Session | UBH", content, current_path="/booking")

# ----------------- Create Stripe Checkout Handler -----------------
@rt("/booking/create-checkout")
async def post_create_checkout(req):
    try:
        form = await req.form()
        slot_id = str(form.get("slot_id", "")).strip()
        artist_name = str(form.get("artist_name", "")).strip()
        artist_email = str(form.get("artist_email", "")).strip()
        phone_number = str(form.get("phone_number", "")).strip()
        package_type = str(form.get("package_type", "studio")).strip()
        session_notes = str(form.get("session_notes", "")).strip()

        # Identify referrer for context-aware redirect
        referer = req.headers.get("referer", "")
        base_path = "/services" if "/services" in referer else "/booking"

        # Validate required inputs
        if not slot_id:
            return RedirectResponse(f"{base_path}?error=Please+select+an+available+time+slot.", status_code=303)

        if not artist_name or not artist_email:
            return RedirectResponse(f"{base_path}?error=Please+provide+both+your+name+and+email+address.", status_code=303)

        slot = get_slot_by_id(slot_id)
        if not slot or slot.get("status") != "available":
            return RedirectResponse(f"{base_path}?error=Selected+slot+is+no+longer+available.+Please+choose+another+time.", status_code=303)

        result = create_checkout_session(
            slot_id=slot_id,
            artist_name=artist_name,
            artist_email=artist_email,
            phone_number=phone_number,
            package_type=package_type,
            session_notes=session_notes
        )

        if "error" in result:
            err_encoded = urllib.parse.quote_plus(str(result["error"]))
            return RedirectResponse(f"{base_path}?error={err_encoded}", status_code=303)

        checkout_url = result.get("url")
        if not checkout_url:
            return RedirectResponse(f"{base_path}?error=Unable+to+generate+checkout+session.", status_code=303)

        # Redirect to Stripe live checkout or mock simulator with 303
        return RedirectResponse(checkout_url, status_code=303)

    except Exception as e:
        print(f"Error in post_create_checkout: {e}")
        return RedirectResponse("/booking?error=A+system+error+occurred+during+checkout+creation.+Please+try+again.", status_code=303)

# ----------------- Mock Checkout for Local Testing -----------------
@rt("/booking/mock-checkout")
def get_mock_checkout(
    session_id: str = "",
    slot_id: str = "",
    artist: str = "",
    email: str = "",
    price: str = "100",
    package: str = "studio",
    package_name: str = ""
):
    if not is_mock_payment_allowed():
        return Response("Mock payment simulation is disabled in this environment.", status_code=403)

    slot = get_slot_by_id(slot_id) or {}
    display_package_name = package_name or (
        "Shadow Talk Podcast (Standard 1-Hr)" if package == "podcast_standard"
        else "Shadow Talk Podcast + Musical Chairs Bundle" if package == "podcast_bundle"
        else f"UBH Studio Recording Session — {slot.get('time_label', '2 Hours')}"
    )

    content = Div(
        Div(
            Div(
                Span("💳 STRIPE CHECKOUT GATEWAY (TEST / DEV SIMULATION)", cls="text-xs font-mono text-[#D4AF37] tracking-widest block mb-2 font-bold"),
                H2("COMPLETE RESERVATION", cls="font-heading text-3xl font-black text-white uppercase mb-4"),
                P("Local simulation mode active. Authorize below to simulate instant Stripe card payment confirmation.", cls="text-neutral-400 text-xs md:text-sm mb-6 leading-relaxed"),
                # Order summary card
                Div(
                    Div(
                        Span("Package / Service:", cls="text-neutral-400 text-xs"),
                        Span(display_package_name, cls="text-white text-xs font-bold text-right max-w-xs"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Date & Time Block:", cls="text-neutral-400 text-xs"),
                        Span(f"{slot.get('date', 'Today')} • {slot.get('time_label', 'Scheduled Time')}", cls="text-white text-xs font-bold"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Artist / Contact:", cls="text-neutral-400 text-xs"),
                        Span(artist or "Independent Artist", cls="text-white text-xs font-bold"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Email Address:", cls="text-neutral-400 text-xs"),
                        Span(email or "artist@domain.com", cls="text-white text-xs font-bold"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Total Amount Due:", cls="text-neutral-300 text-sm font-bold"),
                        Span(f"${price} USD", cls="text-[#D4AF37] text-base font-mono font-bold"),
                        cls="flex justify-between pt-3"
                    ),
                    cls="bg-[#121212] p-5 rounded-xl border border-[#262626] mb-8"
                ),
                # Form to simulate payment
                Form(
                    Input(type="hidden", name="slot_id", value=slot_id),
                    Input(type="hidden", name="artist_name", value=artist),
                    Input(type="hidden", name="artist_email", value=email),
                    Input(type="hidden", name="session_id", value=session_id),
                    Input(type="hidden", name="package_type", value=package),
                    Input(type="hidden", name="package_name", value=display_package_name),
                    Button(
                        f"AUTHORIZE & SIMULATE PAYMENT (${price} USD)",
                        type="submit",
                        cls="btn-gold w-full py-4 text-xs font-heading font-black tracking-widest cursor-pointer mb-3"
                    ),
                    A("Cancel and Return", href="/booking?cancelled=true", cls="text-neutral-500 text-xs hover:text-white block text-center mt-2"),
                    action="/booking/mock-complete",
                    method="POST"
                ),
                cls="bg-[#0D0D0D] border border-[#D4AF37]/50 rounded-2xl p-8 md:p-10 shadow-2xl max-w-lg mx-auto gold-glow"
            ),
            cls="max-w-3xl mx-auto px-6 py-16"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Stripe Checkout Simulation", content, show_nav=True, show_footer=True)

@rt("/booking/mock-complete")
async def post_mock_complete(req):
    if not is_mock_payment_allowed():
        return Response("Mock payment completion is disabled in this environment.", status_code=403)

    try:
        form = await req.form()
        slot_id = form.get("slot_id", "")
        artist_name = form.get("artist_name", "")
        artist_email = form.get("artist_email", "")
        session_id = form.get("session_id", "mock-session-123")
        package_type = form.get("package_type", "studio")
        package_name = form.get("package_name", "")

        if slot_id:
            process_successful_payment(
                slot_id=slot_id,
                artist_name=artist_name,
                artist_email=artist_email,
                package_type=package_type,
                package_name=package_name
            )

        encoded_artist = urllib.parse.quote_plus(artist_name)
        encoded_pkg = urllib.parse.quote_plus(package_name)
        return RedirectResponse(
            f"/booking/success?mock=true&session_id={session_id}&slot_id={slot_id}&artist={encoded_artist}&package_name={encoded_pkg}",
            status_code=303
        )
    except Exception as e:
        print(f"Error in post_mock_complete: {e}")
        return RedirectResponse("/booking?error=Payment+simulation+failed", status_code=303)

# ----------------- Success & Confirmation -----------------
@rt("/booking/success")
def get_booking_success(
    session_id: str = "",
    slot_id: str = "",
    artist: str = "",
    package: str = "",
    package_name: str = "",
    mock: str = ""
):
    slot = get_slot_by_id(slot_id) if slot_id else {}
    display_pkg = package_name or slot.get("package_name") or (
        "Shadow Talk Podcast (Standard 1-Hr)" if package == "podcast_standard"
        else "Shadow Talk Podcast + Musical Chairs Bundle" if package == "podcast_bundle"
        else "UBH Studio Recording Session"
    )

    content = Div(
        Div(
            Div(
                # Success Badge
                Div(
                    Span("✓", cls="text-4xl text-black font-black"),
                    cls="w-16 h-16 rounded-full bg-[#D4AF37] flex items-center justify-center mx-auto mb-6 shadow-lg shadow-[#D4AF37]/30"
                ),
                Span("PAYMENT AUTHORIZED • LOCK CONFIRMED", cls="text-xs font-mono text-[#D4AF37] tracking-[0.3em] block mb-2 font-bold"),
                H1("BOOKING LOCKED IN", cls="font-heading text-3xl sm:text-4xl md:text-5xl font-black text-white uppercase mb-4"),
                P(f"Welcome to the schedule, {artist or 'Artist'}. Your session has been officially registered in the UBH system.", cls="text-neutral-300 text-sm md:text-base mb-8 max-w-lg mx-auto leading-relaxed"),
                # Confirmation Card
                Div(
                    Div(
                        Span("Package Booked:", cls="text-neutral-400 text-xs"),
                        Span(display_pkg, cls="text-[#D4AF37] font-bold text-xs text-right max-w-xs"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Confirmation Ref:", cls="text-neutral-400 text-xs"),
                        Span(session_id[:20] + "..." if len(session_id) > 20 else session_id, cls="text-neutral-300 font-mono text-xs"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Session Date:", cls="text-neutral-400 text-xs"),
                        Span(slot.get("date", datetime.date.today().isoformat()), cls="text-white text-xs font-bold"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Time Block:", cls="text-neutral-400 text-xs"),
                        Span(slot.get("time_label", "Selected Time"), cls="text-white text-xs font-bold"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Status:", cls="text-neutral-400 text-xs"),
                        Span("CONFIRMED & BOOKED", cls="text-emerald-400 font-mono text-xs font-bold"),
                        cls="flex justify-between pt-3"
                    ),
                    cls="bg-[#121212] border border-[#262626] rounded-xl p-6 mb-8 text-left max-w-md mx-auto"
                ),
                # Next steps note
                Div(
                    H4("SESSION PROTOCOL & PREPARATION:", cls="text-xs font-heading font-bold text-[#D4AF37] tracking-wider uppercase mb-2 text-left"),
                    Ul(
                        Li("• Please arrive 10 minutes prior to your time block.", cls="text-xs text-neutral-400"),
                        Li("• For studio sessions: have stems organized on a USB or Cloud drive.", cls="text-xs text-neutral-400"),
                        Li("• For podcast sessions: guest mic check starts 5 minutes before broadcast.", cls="text-xs text-neutral-400"),
                        Li("• Engineer contact and access directions sent to your email.", cls="text-xs text-neutral-400"),
                        cls="space-y-1.5 list-none p-0 text-left mb-8"
                    ),
                    cls="max-w-md mx-auto"
                ),
                A("RETURN TO HOME", href="/", cls="btn-gold py-3 px-8 text-xs font-heading font-black tracking-widest inline-block"),
                cls="bg-[#0D0D0D] border border-[#D4AF37]/40 rounded-2xl p-8 md:p-12 shadow-2xl max-w-2xl mx-auto text-center gold-glow"
            ),
            cls="max-w-4xl mx-auto px-6 py-16"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Booking Confirmed", content, current_path="/booking")

# ----------------- Stripe Webhook -----------------
@rt("/booking/webhook")
async def post_stripe_webhook(req):
    try:
        payload = await req.body()
        sig_header = req.headers.get("stripe-signature", "")

        event = verify_webhook_event(payload, sig_header)
        if not event:
            return Response(content="Invalid signature or payload", status_code=400)

        event_type = event.get("type", "")
        if event_type == "checkout.session.completed":
            session_data = event.get("data", {}).get("object", {})
            metadata = session_data.get("metadata", {})
            slot_id = metadata.get("slot_id")
            artist_name = metadata.get("artist_name", "")
            artist_email = metadata.get("artist_email", "")
            package_type = metadata.get("package_type", "studio")
            package_name = metadata.get("package_name", "")

            if slot_id:
                process_successful_payment(
                    slot_id=slot_id,
                    artist_name=artist_name,
                    artist_email=artist_email,
                    package_type=package_type,
                    package_name=package_name
                )
                print(f"Stripe Webhook: Slot {slot_id} marked booked for {artist_name} ({package_name or package_type})")

        return JSONResponse({"status": "success", "received": True})
    except Exception as e:
        print(f"Error handling Stripe webhook: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
