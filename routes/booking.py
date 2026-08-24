from fasthtml.common import *
from starlette.responses import RedirectResponse, JSONResponse, Response
import urllib.parse
import datetime

from components.base import Layout
from components.calendar import BookingCalendar, RenderSlotOptions
from services.firebase_service import get_slots_for_date, get_slot_by_id
from services.stripe_service import create_checkout_session, process_successful_payment, verify_webhook_event
from config import ENVIRONMENT

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
        slot_id = form.get("slot_id", "").strip()
        artist_name = form.get("artist_name", "").strip()
        artist_email = form.get("artist_email", "").strip()
        phone_number = form.get("phone_number", "").strip()
        package_type = form.get("package_type", "studio").strip()
        session_notes = form.get("session_notes", "").strip()

        if not slot_id or not artist_name or not artist_email:
            return RedirectResponse("/booking?error=Please+select+a+time+slot+and+provide+your+name+and+email.", status_code=303)

        result = create_checkout_session(
            slot_id=slot_id,
            artist_name=artist_name,
            artist_email=artist_email,
            phone_number=phone_number,
            package_type=package_type,
            session_notes=session_notes
        )

        if "error" in result:
            encoded_err = urllib.parse.quote_plus(result["error"])
            return RedirectResponse(f"/booking?error={encoded_err}", status_code=303)

        # Redirect to Stripe Checkout (or Mock Simulator in dev)
        return RedirectResponse(result["url"], status_code=303)

    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return RedirectResponse("/booking?error=An+unexpected+error+occurred.+Please+try+again.", status_code=303)

# ----------------- Mock Checkout Simulator (Dev Only) -----------------
@rt("/booking/mock-checkout")
def get_mock_checkout(
    session_id: str = "",
    slot_id: str = "",
    artist: str = "",
    email: str = "",
    price: int = 100,
    package: str = "studio",
    package_name: str = ""
):
    if ENVIRONMENT == "production":
        return RedirectResponse("/booking?error=Mock+payment+simulator+disabled+in+production", status_code=303)

    slot = get_slot_by_id(slot_id) if slot_id else {}
    display_package_name = package_name or slot.get("package_name") or "UBH Studio Recording Session"

    content = Div(
        Div(
            Div(
                # Badge
                Span("DEV TEST MODE • SIMULATED CHECKOUT", cls="text-xs font-mono text-amber-400 tracking-[0.3em] block mb-2 font-bold"),
                H2("STRIPE CHECKOUT SIMULATOR", cls="font-heading text-2xl sm:text-3xl font-black text-white uppercase mb-4"),
                P("This is a simulated payment gateway for local testing. No real card charge will be made.", cls="text-neutral-400 text-xs md:text-sm mb-6"),
                # Summary Card
                Div(
                    Div(
                        Span("Package:", cls="text-neutral-400 text-xs"),
                        Span(display_package_name, cls="text-[#D4AF37] font-bold text-xs text-right max-w-xs"),
                        cls="flex justify-between py-2 border-b border-[#222222]"
                    ),
                    Div(
                        Span("Scheduled Session:", cls="text-neutral-400 text-xs"),
                        Span(f"{slot.get('date', 'Selected Date')} • {slot.get('time_label', 'Scheduled Time')}", cls="text-white text-xs font-bold"),
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
    if ENVIRONMENT == "production":
        return RedirectResponse("/booking?error=Mock+payment+simulator+disabled+in+production", status_code=303)

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
                print(f"Stripe Webhook: Slot {slot_id} marked booked for {artist_name}")

        return JSONResponse({"status": "success", "received": True})
    except Exception as e:
        print(f"Error handling Stripe webhook: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
