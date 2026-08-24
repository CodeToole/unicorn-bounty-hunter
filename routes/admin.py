from fasthtml.common import *
from starlette.responses import RedirectResponse, JSONResponse
import re
import hmac
import secrets
import datetime
from typing import Optional, Union, Dict, Any

from components.base import Layout
from components.roster import ROSTER_ARTISTS
from config import ADMIN_SECRET_KEY, ADMIN_KEY
from services.firebase_service import (
    get_all_slots_for_date_admin,
    update_slot_status,
    reset_slot_booking,
    add_custom_slot_for_date,
    delete_all_slots_for_date,
    block_entire_day_for_date,
    get_events,
    add_event,
    delete_event,
    get_showcases,
    add_showcase,
    get_subscribers,
    get_all_artist_posts,
    get_artist_posts,
    add_artist_post,
    delete_artist_post,
    create_user_account,
    authenticate_user_account,
    get_all_user_accounts
)

admin_app = FastHTML()
rt = admin_app.route

# ----------------- YouTube ID & URL Helpers -----------------
YOUTUBE_REGEX = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?|shorts)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
    re.IGNORECASE
)
PLAYLIST_REGEX = re.compile(r'[?&]list=([a-zA-Z0-9_-]+)', re.IGNORECASE)
VALID_YT_ID_REGEX = re.compile(r'^[a-zA-Z0-9_-]{11}$')
VALID_RESOURCE_ID_REGEX = re.compile(r'^[a-zA-Z0-9_.-]{1,128}$')

def extract_youtube_id(url_or_id: str) -> tuple[str, bool]:
    """Extracts 11-character YouTube video ID or playlist ID."""
    raw = url_or_id.strip()
    if not raw:
        return "", False

    if "list=" in raw:
        pl_match = PLAYLIST_REGEX.search(raw)
        if pl_match:
            return f"videoseries?list={pl_match.group(1)}", True

    match = YOUTUBE_REGEX.search(raw)
    if match:
        return match.group(1), False

    if VALID_YT_ID_REGEX.match(raw):
        return raw, False

    return "", False

def sanitize_url(url: str) -> str:
    """Ensure URL strictly uses http://, https://, or relative paths, blocking javascript: and unsafe protocols."""
    if not url:
        return ""
    cleaned = url.strip()
    if cleaned.lower().startswith("javascript:") or cleaned.lower().startswith("data:") or cleaned.lower().startswith("vbscript:"):
        return ""
    if cleaned.startswith("/") or cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned
    return ""

def sanitize_resource_id(res_id: str) -> str:
    """Sanitize and validate resource IDs against directory traversal or injection."""
    if not res_id:
        return ""
    cleaned = res_id.strip()
    if VALID_RESOURCE_ID_REGEX.match(cleaned):
        return cleaned
    return ""

# ----------------- Admin Authentication & Session Helpers -----------------

def get_current_user_session(req) -> Optional[Dict[str, Any]]:
    """
    Retrieves user session context from HTTP-only cookies or authorization header.
    Returns dict: {'role': 'super_admin' | 'artist_admin', 'artist_slug': str, 'email': str} or None.
    """
    cookie_token = req.cookies.get("ubh_admin_session", "")
    if cookie_token:
        if hmac.compare_digest(cookie_token, ADMIN_KEY):
            return {"role": "super_admin", "artist_slug": "", "email": "admin@ubh.com"}
        if cookie_token.startswith("artist_admin:"):
            parts = cookie_token.split(":", 2)
            if len(parts) == 3:
                role, artist_slug, email = parts
                return {"role": role, "artist_slug": artist_slug, "email": email}

    # Query param fallback
    key_param = req.query_params.get("key", "")
    if key_param and hmac.compare_digest(key_param, ADMIN_KEY):
        return {"role": "super_admin", "artist_slug": "", "email": "admin@ubh.com"}

    # Authorization header fallback
    auth_header = req.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if hmac.compare_digest(token, ADMIN_KEY):
            return {"role": "super_admin", "artist_slug": "", "email": "admin@ubh.com"}

    return None

def is_admin_authenticated(req) -> bool:
    return get_current_user_session(req) is not None

def is_super_admin(req) -> bool:
    session = get_current_user_session(req)
    return session is not None and session.get("role") == "super_admin"

# ----------------- Admin Routes -----------------

@rt("/admin/login")
async def post_admin_login(req):
    """Handle admin authentication form submission for master key OR multi-tenant user accounts."""
    form = await req.form()
    key = form.get("key", "").strip()
    email = form.get("email", "").strip()
    password = form.get("password", "").strip()

    # 1. Master Key Auth (Super Admin)
    if key and hmac.compare_digest(key, ADMIN_KEY):
        resp = RedirectResponse("/admin?msg=Authenticated+as+Super+Admin", status_code=303)
        resp.set_cookie(
            key="ubh_admin_session",
            value=ADMIN_KEY,
            httponly=True,
            samesite="lax",
            secure=False
        )
        return resp

    # 2. Email / Password Multi-Tenant Auth
    if email and password:
        user = authenticate_user_account(email, password)
        if user:
            role = user.get("role", "artist_admin")
            artist_slug = user.get("artist_slug", "")
            cookie_val = ADMIN_KEY if role == "super_admin" else f"artist_admin:{artist_slug}:{email}"
            resp = RedirectResponse("/admin?tab=posts&msg=Authenticated+successfully", status_code=303)
            resp.set_cookie(
                key="ubh_admin_session",
                value=cookie_val,
                httponly=True,
                samesite="lax",
                secure=False
            )
            return resp

    return RedirectResponse("/admin?error=Invalid+credentials+or+admin+security+key", status_code=303)

@rt("/admin/logout")
def get_admin_logout():
    """Clear admin session cookie and redirect to login."""
    resp = RedirectResponse("/admin?msg=Logged+out+successfully", status_code=303)
    resp.delete_cookie("ubh_admin_session")
    return resp

@rt("/admin")
def get_admin(req, date: str = "", tab: str = "", msg: str = "", error: str = ""):
    # PRE-QUERY AUTH CHECK
    session = get_current_user_session(req)
    if not session:
        # Login View
        login_view = Div(
            Div(
                Span("🔒 ACCESS RESTRICTED", cls="text-xs font-mono text-[#D4AF37] tracking-[0.3em] block mb-2 font-bold"),
                H2("UBH CMS PORTAL", cls="font-heading text-3xl font-black text-white uppercase mb-4"),
                P("Sign in with your Artist Credentials or Master Key to access the console.", cls="text-neutral-400 text-xs md:text-sm mb-6"),
                Div(
                    P(f"❌ {error}", cls="text-rose-400 text-xs font-bold text-center"),
                    cls="mb-6 p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl"
                ) if error else None,
                Div(
                    P(f"✓ {msg}", cls="text-emerald-400 text-xs font-bold text-center"),
                    cls="mb-6 p-3 bg-emerald-950/40 border border-emerald-800/60 rounded-xl"
                ) if msg else None,
                # Dual Mode Form: Master Key OR Email/Password
                Form(
                    H3("ARTIST LOGIN:", cls="text-xs font-heading font-bold text-[#D4AF37] mb-3 text-left uppercase"),
                    Input(
                        type="email",
                        name="email",
                        placeholder="ARTIST EMAIL ADDRESS",
                        cls="input-dark w-full text-xs mb-3 font-mono"
                    ),
                    Input(
                        type="password",
                        name="password",
                        placeholder="PASSWORD",
                        cls="input-dark w-full text-xs mb-4 font-mono"
                    ),
                    Div(cls="border-t border-[#222222] my-4"),
                    H3("OR MASTER KEY:", cls="text-xs font-heading font-bold text-neutral-400 mb-3 text-left uppercase"),
                    Input(
                        type="password",
                        name="key",
                        placeholder="MASTER ADMIN KEY",
                        cls="input-dark w-full text-center tracking-widest text-xs mb-6 font-mono"
                    ),
                    Button(
                        "AUTHENTICATE & ENTER",
                        type="submit",
                        cls="btn-gold w-full text-xs py-3 font-heading font-black tracking-widest cursor-pointer"
                    ),
                    action="/admin/login",
                    method="POST"
                ),
                cls="bg-[#0D0D0D] border border-[#1F1F1F] rounded-2xl p-8 md:p-10 shadow-2xl max-w-md mx-auto text-center"
            ),
            cls="max-w-3xl mx-auto px-6 py-20"
        )
        return Layout("Admin Login", login_view, show_nav=True, show_footer=True, show_capture=False)

    role = session.get("role", "artist_admin")
    assigned_slug = session.get("artist_slug", "")

    # Default tabs depending on role
    if not tab:
        tab = "slots" if role == "super_admin" else "posts"

    # Enforce RBAC for artist_admin
    if role == "artist_admin" and tab != "posts":
        tab = "posts"

    if not date:
        date = datetime.date.today().isoformat()

    # Query required collections based on RBAC
    slots = get_all_slots_for_date_admin(date) if role == "super_admin" else []
    events = get_events() if role == "super_admin" else []
    showcases = get_showcases() if role == "super_admin" else []
    subscribers = get_subscribers() if role == "super_admin" else []
    user_accounts = get_all_user_accounts() if role == "super_admin" else []

    if role == "super_admin":
        all_posts = get_all_artist_posts()
    else:
        all_posts = get_artist_posts(assigned_slug)

    # Nav Tabs
    tabs_list = []
    if role == "super_admin":
        tabs_list.extend([
            A(f"📅 Studio Slots ({date})", href=f"/admin?tab=slots&date={date}", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'slots' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"🎥 YouTube Showcases ({len(showcases)})", href=f"/admin?tab=showcases", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'showcases' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"🎤 Rap Funxtion Events ({len(events)})", href=f"/admin?tab=events", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'events' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"✏️ Artist Posts ({len(all_posts)})", href=f"/admin?tab=posts", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'posts' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"✉️ Subscribers ({len(subscribers)})", href=f"/admin?tab=subscribers", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'subscribers' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"👥 User Accounts ({len(user_accounts)})", href=f"/admin?tab=users", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'users' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        ])
    else:
        tabs_list.append(
            A(f"✏️ My Dispatches & Posts ({len(all_posts)})", href="/admin?tab=posts", cls="px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase bg-[#D4AF37] text-black")
        )

    tabs_header = Div(*tabs_list, cls="flex flex-wrap gap-2 mb-8")

    # 1. Slots Tab Content (Super Admin Only)
    slots_content = Div(
        # Date selector & Bulk Day Actions
        Div(
            Div(
                Form(
                    Label("SELECT DATE TO VIEW & MANAGE SLOTS:", cls="text-xs font-heading font-bold text-neutral-400 uppercase block mb-2"),
                    Div(
                        Input(type="date", name="date", value=date, cls="input-dark text-xs py-2 px-3 font-mono"),
                        Input(type="hidden", name="tab", value="slots"),
                        Button("LOAD DATE", type="submit", cls="btn-gold py-2 px-4 text-xs font-heading font-bold cursor-pointer"),
                        cls="flex gap-2 items-center"
                    ),
                    action="/admin",
                    method="GET"
                ),
                Div(
                    Form(
                        Input(type="hidden", name="date", value=date),
                        Button("⚠️ WIPE ALL SLOTS FOR DATE", type="submit", cls="text-[10px] bg-rose-950 text-rose-400 hover:bg-rose-900 border border-rose-800/80 px-3 py-2 rounded font-mono font-bold cursor-pointer"),
                        action="/admin/slots/wipe-day",
                        method="POST"
                    ),
                    Form(
                        Input(type="hidden", name="date", value=date),
                        Button("🚫 BLOCK ENTIRE DAY (CLOSED)", type="submit", cls="text-[10px] bg-amber-950 text-amber-400 hover:bg-amber-900 border border-amber-800/80 px-3 py-2 rounded font-mono font-bold cursor-pointer"),
                        action="/admin/slots/block-day",
                        method="POST"
                    ),
                    cls="flex flex-wrap gap-2 items-center mt-4 md:mt-0"
                ),
                cls="flex flex-col md:flex-row justify-between md:items-end p-4 bg-[#121212] border border-[#222222] rounded-xl mb-6"
            ),
            # Custom Slot Creation Form
            Div(
                H3("ADD CUSTOM TIME SLOT FOR DATE", cls="font-heading font-bold text-xs text-[#D4AF37] uppercase mb-3"),
                Form(
                    Input(type="hidden", name="date", value=date),
                    Div(
                        Div(
                            Label("TIME LABEL:", cls="text-[10px] font-heading font-bold text-neutral-400 block mb-1"),
                            Input(type="text", name="time_label", placeholder="e.g. 10:00 AM – 1:00 PM (3 Hours)", required=True, cls="input-dark text-xs py-1.5 px-3 w-full"),
                            cls="flex-grow mb-2 sm:mb-0"
                        ),
                        Div(
                            Label("DURATION (HRS):", cls="text-[10px] font-heading font-bold text-neutral-400 block mb-1"),
                            Input(type="number", name="duration", value="2", required=True, cls="input-dark text-xs py-1.5 px-3 w-24"),
                            cls="mb-2 sm:mb-0"
                        ),
                        Div(
                            Label("PRICE ($ USD):", cls="text-[10px] font-heading font-bold text-neutral-400 block mb-1"),
                            Input(type="number", name="price", value="100", required=True, cls="input-dark text-xs py-1.5 px-3 w-28"),
                            cls="mb-2 sm:mb-0"
                        ),
                        Button("ADD CUSTOM SLOT", type="submit", cls="btn-gold text-xs py-2 px-4 font-heading font-bold cursor-pointer mt-4 sm:mt-0 self-end"),
                        cls="flex flex-col sm:flex-row gap-3 items-stretch sm:items-end"
                    ),
                    action="/admin/slots/add-custom",
                    method="POST",
                    cls="p-4 bg-[#121212] border border-[#222222] rounded-xl mb-6"
                )
            ),
            # Slots Grid
            Div(
                *[
                    Div(
                        Div(
                            Span(slot.get("time_label", ""), cls="font-heading font-bold text-sm text-white"),
                            Span(
                                slot.get("status", "available").upper(),
                                cls=f"text-[10px] font-mono font-bold px-2 py-0.5 rounded uppercase { 'bg-emerald-950 text-emerald-400 border border-emerald-800' if slot.get('status') == 'available' else 'bg-rose-950 text-rose-400 border border-rose-800' }"
                            ),
                            cls="flex justify-between items-center mb-3"
                        ),
                        Div(
                            P(f"Artist: {slot.get('artist_name', 'None')}", cls="text-xs text-neutral-300 font-bold"),
                            P(f"Email: {slot.get('artist_email', 'None')}", cls="text-xs text-neutral-400 font-mono"),
                            P(f"Package: {slot.get('package_name', slot.get('package_type', 'Studio Session'))}", cls="text-xs text-[#D4AF37]"),
                            cls="mb-4 p-3 bg-[#0A0A0A] rounded-lg border border-[#1F1F1F]"
                        ) if slot.get("status") == "booked" else P(f"Price: ${slot.get('price', 100)} USD | Duration: {slot.get('duration', 2)} hrs", cls="text-xs text-neutral-400 italic mb-4"),
                        # Quick Status Toggle Form
                        Form(
                            Input(type="hidden", name="slot_id", value=slot.get("id", "")),
                            Input(type="hidden", name="date", value=date),
                            Div(
                                Select(
                                    Option("Available", value="available", selected=(slot.get("status") == "available")),
                                    Option("Booked / Locked", value="booked", selected=(slot.get("status") == "booked")),
                                    Option("Maintenance / Blocked", value="maintenance", selected=(slot.get("status") == "maintenance")),
                                    name="status",
                                    cls="input-dark text-xs py-1.5 px-2 font-mono flex-grow"
                                ),
                                Button("UPDATE", type="submit", cls="btn-gold py-1.5 px-3 text-[10px] font-heading font-bold cursor-pointer"),
                                cls="flex gap-2 mb-2"
                            ),
                            action="/admin/slots/update",
                            method="POST"
                        ),
                        # Clear/Reset Booking Form
                        Form(
                            Input(type="hidden", name="slot_id", value=slot.get("id", "")),
                            Input(type="hidden", name="date", value=date),
                            Button("🗑️ Clear / Delete Booking", type="submit", cls="w-full text-center text-[10px] text-rose-400 hover:text-rose-300 font-heading font-bold tracking-wider py-1 cursor-pointer bg-transparent border-0 hover:underline"),
                            action="/admin/slots/delete",
                            method="POST"
                        ) if slot.get("status") == "booked" else None,
                        cls="p-4 bg-[#141414] border border-[#262626] rounded-xl"
                    )
                    for slot in slots
                ] if slots else [P("No slots configured for this date.", cls="text-neutral-500 text-xs italic p-4")],
                cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            )
        )
    )

    # 2. Showcases Tab Content (Super Admin Only)
    showcases_content = Div(
        Div(
            H3("ADD NEW YOUTUBE SHOWCASE", cls="font-heading font-bold text-sm text-[#D4AF37] uppercase mb-4"),
            Form(
                Div(
                    Label("SHOWCASE TITLE:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="title", placeholder="e.g. Rap Funxtion Cypher Vol. 16", required=True, cls="input-dark w-full text-xs"),
                    cls="mb-3"
                ),
                Div(
                    Label("YOUTUBE URL OR VIDEO ID:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="youtube_url", placeholder="https://www.youtube.com/watch?v=... or 11-char ID", required=True, cls="input-dark w-full text-xs font-mono"),
                    cls="mb-3"
                ),
                Div(
                    Label("DESCRIPTION:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Textarea(name="description", placeholder="Brief description...", rows="3", cls="input-dark w-full text-xs font-body"),
                    cls="mb-4"
                ),
                Button("PUBLISH SHOWCASE", type="submit", cls="btn-gold py-2.5 px-6 text-xs font-heading font-black cursor-pointer"),
                action="/admin/showcases/add",
                method="POST"
            ),
            cls="bg-[#121212] border border-[#222222] p-6 rounded-xl mb-8"
        ),
        Div(
            Span(f"PUBLISHED SHOWCASES: {len(showcases)}", cls="text-xs font-mono font-bold text-[#D4AF37] tracking-wider uppercase block mb-4"),
            Div(
                *[
                    Div(
                        H4(sc.get("title", "Untitled"), cls="font-heading font-bold text-sm text-white mb-1"),
                        P(f"ID: {sc.get('youtube_id', '')}", cls="text-neutral-400 text-xs font-mono mb-2"),
                        P(sc.get("description", ""), cls="text-neutral-400 text-xs mb-3"),
                        cls="p-4 bg-[#141414] border border-[#262626] rounded-xl"
                    )
                    for sc in showcases
                ] if showcases else [P("No showcases added yet.", cls="text-neutral-500 text-xs italic")],
                cls="space-y-3"
            ),
            cls="p-6 bg-[#121212] border border-[#222222] rounded-xl"
        )
    )

    # 3. Events Tab Content (Super Admin Only)
    events_content = Div(
        Div(
            H3("ADD RAP FUNXTION LIVE EVENT", cls="font-heading font-bold text-sm text-[#D4AF37] uppercase mb-4"),
            Form(
                Div(
                    Label("EVENT TITLE:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="title", placeholder="e.g. RAP FUNXTION 17 — LIVE AT THE VAULT", required=True, cls="input-dark w-full text-xs"),
                    cls="mb-3"
                ),
                Div(
                    Label("EVENT DATE:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="date", placeholder="e.g. Saturday, Oct 24, 2026", required=True, cls="input-dark w-full text-xs"),
                    cls="mb-3"
                ),
                Div(
                    Label("STATUS:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="status", placeholder="Active / Sold Out / Coming Soon", value="Active", cls="input-dark w-full text-xs"),
                    cls="mb-3"
                ),
                Div(
                    Label("FLYER IMAGE URL:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="flyer_url", placeholder="/static/assets/rf16_flyer_new.jpg", cls="input-dark w-full text-xs font-mono"),
                    cls="mb-3"
                ),
                Div(
                    Label("TICKET URL:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="ticket_url", placeholder="https://...", cls="input-dark w-full text-xs font-mono"),
                    cls="mb-3"
                ),
                Div(
                    Label("DESCRIPTION:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Textarea(name="description", placeholder="Lineup, venue info, doors open time...", rows="3", cls="input-dark w-full text-xs font-body"),
                    cls="mb-4"
                ),
                Button("PUBLISH EVENT", type="submit", cls="btn-gold py-2.5 px-6 text-xs font-heading font-black cursor-pointer"),
                action="/admin/events/add",
                method="POST"
            ),
            cls="bg-[#121212] border border-[#222222] p-6 rounded-xl mb-8"
        ),
        Div(
            Span(f"REGISTERED EVENTS: {len(events)}", cls="text-xs font-mono font-bold text-[#D4AF37] tracking-wider uppercase block mb-4"),
            Div(
                *[
                    Div(
                        Div(
                            H4(ev.get("title", "Untitled"), cls="font-heading font-bold text-sm text-white mb-1"),
                            Span(ev.get("status", "Active"), cls="text-[10px] font-mono text-[#D4AF37] bg-[#1A1A1A] px-2 py-0.5 rounded"),
                            cls="flex justify-between items-center mb-2"
                        ),
                        P(f"Date: {ev.get('date', 'TBD')}", cls="text-neutral-400 text-xs mb-2"),
                        P(ev.get("description", ""), cls="text-neutral-400 text-xs mb-3"),
                        Form(
                            Input(type="hidden", name="event_id", value=ev.get("id", "")),
                            Button("🗑️ Delete Event", type="submit", cls="text-[10px] text-rose-400 hover:text-rose-300 font-heading font-bold tracking-wider cursor-pointer bg-transparent border-0 p-0 hover:underline"),
                            action="/admin/events/delete",
                            method="POST"
                        ),
                        cls="p-4 bg-[#141414] border border-[#262626] rounded-xl"
                    )
                    for ev in events
                ] if events else [P("No events added yet.", cls="text-neutral-500 text-xs italic")],
                cls="space-y-3"
            ),
            cls="p-6 bg-[#121212] border border-[#222222] rounded-xl"
        )
    )

    # 4. Posts Tab Content (Filtered by RBAC)
    if role == "super_admin":
        artist_slug_options = [
            Option(f"{art['name']} ({art['slug']})", value=art['slug'])
            for art in ROSTER_ARTISTS
        ]
        artist_select_element = Select(
            *artist_slug_options,
            name="artist_slug",
            required=True,
            cls="input-dark w-full text-xs py-2"
        )
    else:
        # Artist Admin: fixed to assigned slug
        artist_select_element = Div(
            Input(type="hidden", name="artist_slug", value=assigned_slug),
            P(f"Publishing as: {assigned_slug.upper()}", cls="text-xs font-mono font-bold text-[#D4AF37] p-2 bg-[#1A1A1A] rounded border border-[#2A2A2A]")
        )

    posts_content = Div(
        Div(
            H3("PUBLISH ARTIST POST / DISPATCH", cls="font-heading font-bold text-sm text-[#D4AF37] uppercase mb-4"),
            Form(
                Div(
                    Label("ARTIST PROFILE:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    artist_select_element,
                    cls="mb-3"
                ),
                Div(
                    Label("POST TITLE:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="title", placeholder="Post headline...", required=True, cls="input-dark w-full text-xs"),
                    cls="mb-3"
                ),
                Div(
                    Label("BODY:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Textarea(name="body", placeholder="Full post content. Use blank lines for paragraphs.", rows="5", required=True, cls="input-dark w-full text-xs font-body"),
                    cls="mb-3"
                ),
                Div(
                    Label("MEDIA URL (OPTIONAL):", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="text", name="media_url", placeholder="/static/assets/image.jpg or https://...", cls="input-dark w-full text-xs font-mono"),
                    cls="mb-4"
                ),
                Button("PUBLISH POST", type="submit", cls="btn-gold py-2.5 px-6 text-xs font-heading font-black cursor-pointer"),
                action="/admin/posts/add",
                method="POST"
            ),
            cls="bg-[#121212] border border-[#222222] p-6 rounded-xl mb-8"
        ),
        Div(
            Span(f"PUBLISHED POSTS ({assigned_slug.upper() if assigned_slug else 'ALL'}): {len(all_posts)}", cls="text-xs font-mono font-bold text-[#D4AF37] tracking-wider uppercase block mb-4"),
            Div(
                *[
                    Div(
                        Div(
                            Span(p.get('artist_slug', '').upper(), cls="text-[9px] font-mono font-bold tracking-wider px-2 py-0.5 rounded bg-[#D4AF37]/10 text-[#D4AF37] mr-2"),
                            Span(p.get('created_at', '')[:10], cls="text-[10px] font-mono text-neutral-500"),
                            cls="flex items-center gap-2 mb-2"
                        ),
                        H4(p.get('title', 'Untitled'), cls="font-heading font-bold text-sm text-white mb-1"),
                        P(p.get('body', '')[:120] + ('...' if len(p.get('body', '')) > 120 else ''), cls="text-neutral-400 text-xs mb-3"),
                        Div(
                            A(f"View on profile →", href=f"/roster/{p.get('artist_slug')}#post-{p.get('id')}", cls="text-[10px] text-[#D4AF37] hover:text-[#FFD700] font-heading font-bold tracking-wider"),
                            Form(
                                Input(type="hidden", name="post_id", value=p.get('id', '')),
                                Button("🗑️ Delete Post", type="submit", cls="text-[10px] text-rose-400 hover:text-rose-300 font-heading font-bold tracking-wider cursor-pointer bg-transparent border-0 p-0 hover:underline"),
                                action="/admin/posts/delete",
                                method="POST",
                                cls="inline"
                            ),
                            cls="flex items-center justify-between mt-2 pt-2 border-t border-[#222222]"
                        ),
                        cls="p-4 bg-[#141414] border border-[#262626] rounded-xl"
                    )
                    for p in all_posts
                ] if all_posts else [P("No posts published yet. Use the form above to create the first one.", cls="text-neutral-500 text-xs italic")],
                cls="space-y-3 max-h-[600px] overflow-y-auto"
            ),
            cls="p-6 bg-[#121212] border border-[#222222] rounded-xl"
        )
    )

    # 5. Subscribers Tab Content (Super Admin Only)
    subscribers_content = Div(
        Span(f"TOTAL REGISTERED SUBSCRIBERS: {len(subscribers)}", cls="text-xs font-mono font-bold text-[#D4AF37] tracking-wider uppercase block mb-4"),
        Div(
            *[
                Div(
                    Span(sub.get("email", ""), cls="font-mono text-xs text-white font-bold"),
                    Span(sub.get("created_at", "")[:10], cls="font-mono text-[10px] text-neutral-500"),
                    cls="flex justify-between items-center p-3 bg-[#141414] border border-[#262626] rounded-lg"
                )
                for sub in subscribers
            ] if subscribers else [P("No subscribers registered yet.", cls="text-neutral-500 text-xs italic")],
            cls="space-y-2 max-h-[600px] overflow-y-auto"
        ),
        cls="p-6 bg-[#121212] border border-[#222222] rounded-xl"
    )

    # 6. User Accounts Tab Content (Super Admin Only)
    users_content = Div(
        # Create User Account Form
        Div(
            H3("CREATE ARTIST ADMIN ACCOUNT", cls="font-heading font-bold text-sm text-[#D4AF37] uppercase mb-4"),
            Form(
                Div(
                    Label("USER EMAIL ADDRESS:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="email", name="email", placeholder="artist@ubh.com", required=True, cls="input-dark w-full text-xs font-mono"),
                    cls="mb-3"
                ),
                Div(
                    Label("PASSWORD:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="password", name="password", placeholder="Assign secure password...", required=True, cls="input-dark w-full text-xs font-mono"),
                    cls="mb-3"
                ),
                Div(
                    Label("ROLE:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Select(
                        Option("Artist Admin", value="artist_admin"),
                        Option("Super Admin", value="super_admin"),
                        name="role",
                        cls="input-dark w-full text-xs py-2"
                    ),
                    cls="mb-3"
                ),
                Div(
                    Label("ASSIGNED ARTIST SLUG:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Select(
                        *[Option(f"{art['name']} ({art['slug']})", value=art['slug']) for art in ROSTER_ARTISTS],
                        name="artist_slug",
                        cls="input-dark w-full text-xs py-2"
                    ),
                    cls="mb-4"
                ),
                Button("CREATE ARTIST ACCOUNT", type="submit", cls="btn-gold py-2.5 px-6 text-xs font-heading font-black cursor-pointer"),
                action="/admin/users/create",
                method="POST"
            ),
            cls="bg-[#121212] border border-[#222222] p-6 rounded-xl mb-8"
        ),
        # Existing User Accounts List
        Div(
            Span(f"REGISTERED USER ACCOUNTS: {len(user_accounts)}", cls="text-xs font-mono font-bold text-[#D4AF37] tracking-wider uppercase block mb-4"),
            Div(
                *[
                    Div(
                        Div(
                            Span(usr.get("email", ""), cls="font-mono text-xs text-white font-bold"),
                            Span(usr.get("role", "").upper(), cls="text-[10px] font-mono text-[#D4AF37] bg-[#1A1A1A] px-2 py-0.5 rounded"),
                            cls="flex justify-between items-center mb-1"
                        ),
                        P(f"Assigned Slug: {usr.get('artist_slug', 'None (Super Admin)')}", cls="text-neutral-400 text-xs font-mono"),
                        cls="p-3 bg-[#141414] border border-[#262626] rounded-lg"
                    )
                    for usr in user_accounts
                ] if user_accounts else [P("No user accounts created yet.", cls="text-neutral-500 text-xs italic")],
                cls="space-y-2"
            ),
            cls="p-6 bg-[#121212] border border-[#222222] rounded-xl"
        )
    )

    tab_map = {
        'slots': slots_content,
        'showcases': showcases_content,
        'events': events_content,
        'posts': posts_content,
        'subscribers': subscribers_content,
        'users': users_content
    }
    active_tab_content = tab_map.get(tab, posts_content if role == 'artist_admin' else slots_content)

    dashboard = Div(
        Div(
            # Header
            Div(
                Div(
                    Span(f"⚡ UBH CONSOLE — {'SUPER ADMIN' if role == 'super_admin' else f'ARTIST PORTAL ({assigned_slug.upper()})'}", cls="text-xs font-mono text-[#D4AF37] tracking-[0.3em] font-bold block mb-1"),
                    H1("ADMIN CMS ENGINE", cls="font-heading text-3xl sm:text-4xl font-black text-white uppercase"),
                    cls="flex-grow"
                ),
                A("LOG OUT", href="/admin/logout", cls="btn-gold-outline text-xs py-1.5 px-4 font-heading"),
                cls="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 border-b border-[#1A1A1A] pb-6"
            ),
            Div(
                P(f"✓ {msg}", cls="text-emerald-400 text-xs font-bold text-center"),
                cls="mb-6 p-3 bg-emerald-950/40 border border-emerald-800/60 rounded-xl"
            ) if msg else None,
            Div(
                P(f"❌ {error}", cls="text-rose-400 text-xs font-bold text-center"),
                cls="mb-6 p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl"
            ) if error else None,
            tabs_header,
            active_tab_content,
            cls="max-w-6xl mx-auto px-6 py-10"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Admin CMS Engine", dashboard, show_nav=True, show_footer=True, show_capture=False)

# ----------------- Admin Action Handlers -----------------

@rt("/admin/slots/add-custom")
async def post_admin_slot_add_custom(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    date = form.get("date", "").strip()
    time_label = form.get("time_label", "").strip()
    duration = int(form.get("duration", "2"))
    price = int(form.get("price", "100"))

    if date and time_label:
        add_custom_slot_for_date(date_str=date, time_label=time_label, duration=duration, price=price)
    return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Custom+slot+added+successfully", status_code=303)

@rt("/admin/slots/wipe-day")
async def post_admin_slot_wipe_day(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    date = form.get("date", "").strip()
    if date:
        delete_all_slots_for_date(date)
    return RedirectResponse(f"/admin?tab=slots&date={date}&msg=All+slots+wiped+for+{date}", status_code=303)

@rt("/admin/slots/block-day")
async def post_admin_slot_block_day(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    date = form.get("date", "").strip()
    if date:
        block_entire_day_for_date(date)
    return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Entire+day+blocked+for+{date}", status_code=303)

@rt("/admin/slots/update")
async def post_admin_slot_update(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    slot_id = sanitize_resource_id(form.get("slot_id", ""))
    status = form.get("status", "available").strip()
    date = form.get("date", "").strip()

    if slot_id:
        update_slot_status(slot_id, status)
    return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Slot+status+updated+to+{status}", status_code=303)

@rt("/admin/slots/delete")
async def post_admin_slot_delete(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    slot_id = sanitize_resource_id(form.get("slot_id", ""))
    date = form.get("date", "").strip()

    if slot_id:
        reset_slot_booking(slot_id)
    return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Booking+deleted+and+slot+re-opened", status_code=303)

@rt("/admin/users/create")
async def post_admin_user_create(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    email = form.get("email", "").strip()
    password = form.get("password", "").strip()
    role = form.get("role", "artist_admin").strip()
    artist_slug = form.get("artist_slug", "").strip()

    if email and password:
        create_user_account(email=email, password=password, role=role, artist_slug=artist_slug)
        return RedirectResponse(f"/admin?tab=users&msg=User+account+created+for+{email}", status_code=303)

    return RedirectResponse("/admin?tab=users&error=Email+and+password+are+required", status_code=303)

@rt("/admin/showcases/add")
async def post_admin_showcase_add(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    title = form.get("title", "").strip()
    youtube_url = form.get("youtube_url", "").strip()
    description = form.get("description", "").strip()

    yt_id, is_playlist = extract_youtube_id(youtube_url)
    if not yt_id:
        return RedirectResponse("/admin?tab=showcases&error=Invalid+YouTube+URL+or+Video+ID", status_code=303)

    add_showcase(title=title, youtube_id=yt_id, description=description, is_playlist=is_playlist)
    return RedirectResponse("/admin?tab=showcases&msg=Showcase+published+successfully", status_code=303)

@rt("/admin/events/add")
async def post_admin_event_add(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    title = form.get("title", "").strip()
    date = form.get("date", "").strip()
    status = form.get("status", "Active").strip()
    flyer_url = sanitize_url(form.get("flyer_url", "").strip())
    ticket_url = sanitize_url(form.get("ticket_url", "").strip())
    description = form.get("description", "").strip()

    add_event(
        title=title,
        date=date,
        status=status,
        flyer_url=flyer_url,
        ticket_url=ticket_url,
        description=description
    )
    return RedirectResponse("/admin?tab=events&msg=Event+added+successfully", status_code=303)

@rt("/admin/events/delete")
async def post_admin_event_delete(req):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    event_id = sanitize_resource_id(form.get("event_id", ""))

    if event_id:
        delete_event(event_id)
    return RedirectResponse("/admin?tab=events&msg=Event+deleted+successfully", status_code=303)

@rt("/admin/posts/add")
async def post_admin_artist_post(req):
    session = get_current_user_session(req)
    if not session:
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    role = session.get("role", "artist_admin")
    assigned_slug = session.get("artist_slug", "")

    if role == "artist_admin":
        artist_slug = assigned_slug
    else:
        artist_slug = form.get("artist_slug", "").strip()

    title = form.get("title", "").strip()
    body = form.get("body", "").strip()
    media_url = sanitize_url(form.get("media_url", "").strip())

    if not artist_slug or not title or not body:
        return RedirectResponse("/admin?tab=posts&error=Title+and+body+are+required", status_code=303)

    add_artist_post(artist_slug=artist_slug, title=title, body=body, media_url=media_url)
    return RedirectResponse(f"/admin?tab=posts&msg=Post+published+for+{artist_slug}", status_code=303)

@rt("/admin/posts/delete")
async def post_admin_artist_post_delete(req):
    session = get_current_user_session(req)
    if not session:
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    post_id = sanitize_resource_id(form.get("post_id", ""))
    role = session.get("role", "artist_admin")
    assigned_slug = session.get("artist_slug", "")

    if post_id:
        if role == "artist_admin":
            # Verify post belongs to assigned artist slug before deletion
            all_posts = get_artist_posts(assigned_slug)
            if any(p.get("id") == post_id for p in all_posts):
                delete_artist_post(post_id)
            else:
                return RedirectResponse("/admin?tab=posts&error=Unauthorized+to+delete+this+post", status_code=303)
        else:
            delete_artist_post(post_id)

    return RedirectResponse("/admin?tab=posts&msg=Post+deleted+successfully", status_code=303)
