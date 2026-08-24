from fasthtml.common import *
from starlette.responses import RedirectResponse, JSONResponse, Response
from starlette.requests import Request
import re
import datetime
import hashlib
import hmac
import secrets
from typing import Optional, Union, Dict, Any

from components.base import Layout
from components.roster import ROSTER_ARTISTS
from config import ADMIN_SECRET_KEY, ADMIN_KEY, IS_PRODUCTION
from services.firebase_service import (
    get_all_slots_for_date_admin,
    get_slot_by_id,
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

SESSION_COOKIE_NAME = "ubh_admin_session"

# ----------------- Auth & Session Cookie Helpers -----------------

def get_session_token() -> str:
    """Derives a secure session token HMAC from ADMIN_SECRET_KEY."""
    if not ADMIN_SECRET_KEY:
        return ""
    return hmac.new(
        ADMIN_SECRET_KEY.encode("utf-8"),
        b"ubh_admin_session_v1",
        hashlib.sha256
    ).hexdigest()

def get_current_user_session(req: Request) -> Optional[Dict[str, Any]]:
    """
    Retrieves user session context from HTTP-only cookies, Authorization header, or query params.
    Returns dict: {'role': 'super_admin' | 'artist_admin', 'artist_slug': str, 'email': str} or None.
    """
    cookie_token = req.cookies.get(SESSION_COOKIE_NAME, "")
    if cookie_token:
        # Check Super Admin Master Token or Secret Key
        if ADMIN_SECRET_KEY and (hmac.compare_digest(cookie_token, ADMIN_SECRET_KEY) or hmac.compare_digest(cookie_token, get_session_token())):
            return {"role": "super_admin", "artist_slug": "", "email": "admin@ubh.com"}
        # Check Artist Admin Cookie
        if cookie_token.startswith("artist_admin:"):
            parts = cookie_token.split(":", 2)
            if len(parts) == 3:
                role, artist_slug, email = parts
                return {"role": role, "artist_slug": artist_slug, "email": email}

    # Authorization Bearer header check
    auth_header = req.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if ADMIN_SECRET_KEY and (hmac.compare_digest(token, ADMIN_SECRET_KEY) or hmac.compare_digest(token, get_session_token())):
            return {"role": "super_admin", "artist_slug": "", "email": "admin@ubh.com"}

    # Query param fallback for backwards compatibility
    key_param = req.query_params.get("key", "").strip()
    if key_param and ADMIN_SECRET_KEY and hmac.compare_digest(key_param, ADMIN_SECRET_KEY):
        return {"role": "super_admin", "artist_slug": "", "email": "admin@ubh.com"}

    return None

def is_admin_authenticated(req: Request) -> bool:
    """Enforces strict pre-query authentication check."""
    return get_current_user_session(req) is not None

def is_super_admin(req: Request) -> bool:
    """Checks if current request is authenticated as super_admin."""
    session = get_current_user_session(req)
    return session is not None and session.get("role") == "super_admin"

# ----------------- Input Sanitization & Media Protocol Checks -----------------

def sanitize_media_url(url: str, allow_relative: bool = True, allow_hash: bool = False) -> str:
    """
    Sanitizes user-supplied media URLs to strictly require http://, https://,
    or relative /static/ paths. Explicitly rejects javascript: or malformed URLs.
    """
    if not url:
        return ""
    raw = str(url).strip()
    if not raw:
        return ""

    if allow_hash and raw == "#":
        return "#"

    lower = raw.lower()
    if lower.startswith(("javascript:", "data:", "vbscript:")) or any(ord(c) < 32 for c in raw):
        return ""

    if raw.startswith("https://") or raw.startswith("http://"):
        if re.match(r'^https?://[^\s<>"]+$', raw):
            return raw
        return ""

    if allow_relative and (raw.startswith("/static/") or raw.startswith("/")):
        if ".." not in raw and re.match(r'^/[^\s<>"]+$', raw):
            return raw
        return ""

    return ""

def sanitize_url(url: str) -> str:
    """Alias for sanitize_media_url."""
    return sanitize_media_url(url, allow_relative=True, allow_hash=True)

def sanitize_identifier(ident: str, max_length: int = 128) -> str:
    """Sanitizes IDs (slot_id, event_id, post_id) to strict alphanumeric, hyphen, underscore, dot."""
    if not ident:
        return ""
    raw = str(ident).strip()
    if re.match(r'^[a-zA-Z0-9_.-]+$', raw) and len(raw) <= max_length:
        return raw
    return ""

def sanitize_resource_id(res_id: str) -> str:
    """Alias for sanitize_identifier."""
    return sanitize_identifier(res_id)

# ----------------- YouTube ID Regex Extractor -----------------
YOUTUBE_REGEX = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?|shorts)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
    re.IGNORECASE
)
PLAYLIST_REGEX = re.compile(r'[?&]list=([a-zA-Z0-9_-]+)', re.IGNORECASE)

def extract_youtube_id(url_or_id: str) -> tuple[str, bool]:
    """
    Extracts strictly validated 11-character YouTube video ID or playlist ID from pasted URL.
    Returns (extracted_id, is_playlist). If invalid, returns ("", False).
    """
    raw = str(url_or_id).strip()
    if not raw:
        return "", False

    if raw.lower().startswith("javascript:"):
        return "", False

    if "list=" in raw:
        pl_match = PLAYLIST_REGEX.search(raw)
        if pl_match:
            playlist_id = pl_match.group(1)
            if re.match(r'^[a-zA-Z0-9_-]+$', playlist_id):
                return f"videoseries?list={playlist_id}", True

    match = YOUTUBE_REGEX.search(raw)
    if match:
        yt_id = match.group(1)
        if len(yt_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', yt_id):
            return yt_id, False

    if len(raw) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', raw):
        return raw, False

    return "", False

# ----------------- Authentication Routes -----------------

@rt("/admin/login")
async def post_admin_login(req: Request):
    """Handles dual-mode authentication (Master Admin Key OR Artist Email/Password)."""
    form = await req.form()
    key = str(form.get("key", "")).strip()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", "")).strip()

    # 1. Master Key Auth (Super Admin)
    if ADMIN_SECRET_KEY and key and hmac.compare_digest(key, ADMIN_SECRET_KEY):
        resp = RedirectResponse("/admin?msg=Authenticated+as+Super+Admin", status_code=303)
        resp.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=ADMIN_SECRET_KEY,
            httponly=True,
            samesite="lax",
            secure=IS_PRODUCTION,
            max_age=86400,
            path="/"
        )
        return resp

    # 2. Multi-Tenant Email & Password Auth (Artist Admin or Super Admin)
    if email and password:
        user = authenticate_user_account(email, password)
        if user:
            role = user.get("role", "artist_admin")
            artist_slug = user.get("artist_slug", "")
            cookie_val = ADMIN_SECRET_KEY if role == "super_admin" else f"artist_admin:{artist_slug}:{email}"
            target_tab = "slots" if role == "super_admin" else "posts"
            resp = RedirectResponse(f"/admin?tab={target_tab}&msg=Authenticated+successfully", status_code=303)
            resp.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=cookie_val,
                httponly=True,
                samesite="lax",
                secure=IS_PRODUCTION,
                max_age=86400,
                path="/"
            )
            return resp

    return RedirectResponse("/admin?error=Invalid+credentials+or+admin+security+key", status_code=303)

@rt("/admin/logout")
def get_admin_logout():
    """Clears admin session cookie and redirects to login portal."""
    resp = RedirectResponse("/admin?msg=Logged+out+successfully", status_code=303)
    resp.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return resp

# ----------------- Admin CMS Dashboard -----------------

@rt("/admin")
def get_admin(req: Request, date: str = "", tab: str = "", msg: str = "", error: str = ""):
    session = get_current_user_session(req)

    # PRE-QUERY AUTH CHECK: Show Login Form without querying any database models
    if not session:
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
                # Dual Mode Login Form
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

    # Default tab based on role
    if not tab:
        tab = "slots" if role == "super_admin" else "posts"

    # Enforce RBAC: artist_admin cannot view other tabs
    if role == "artist_admin" and tab != "posts":
        tab = "posts"

    if not date:
        date = datetime.date.today().isoformat()

    # Query only authorized data based on role
    slots = get_all_slots_for_date_admin(date) if role == "super_admin" else []
    events = get_events() if role == "super_admin" else []
    showcases = get_showcases() if role == "super_admin" else []
    subscribers = get_subscribers() if role == "super_admin" else []
    user_accounts = get_all_user_accounts() if role == "super_admin" else []

    if role == "super_admin":
        all_posts = get_all_artist_posts()
    else:
        all_posts = get_artist_posts(assigned_slug)

    # Build Navigation Tabs
    tabs_list = []
    if role == "super_admin":
        tabs_list.extend([
            A(f"📅 Studio Slots ({date})", href=f"/admin?tab=slots&date={date}", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'slots' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"🎥 Showcases ({len(showcases)})", href="/admin?tab=showcases", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'showcases' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"🎤 Events ({len(events)})", href="/admin?tab=events", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'events' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"✏️ Artist Posts ({len(all_posts)})", href="/admin?tab=posts", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'posts' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"✉️ Subscribers ({len(subscribers)})", href="/admin?tab=subscribers", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'subscribers' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
            A(f"👥 User Accounts ({len(user_accounts)})", href="/admin?tab=users", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'users' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        ])
    else:
        tabs_list.append(
            A(f"✏️ My Dispatches & Posts ({len(all_posts)})", href="/admin?tab=posts", cls="px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase bg-[#D4AF37] text-black")
        )

    tabs_header = Div(*tabs_list, cls="flex flex-wrap gap-2 mb-8")

    # 1. Studio Slots Tab Content (Super Admin Only)
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
                ] if slots else [P("No slots configured for this date. Use the 'ADD CUSTOM SLOT' form above to create slots.", cls="text-neutral-500 text-xs italic p-4")],
                cls="grid grid-cols-1 md:grid-cols-2 gap-4"
            )
        )
    )

    # 2. Showcases Tab Content (Super Admin Only)
    showcases_content = Div(
        Div(
            H3("ADD YOUTUBE SHOWCASE / CYPHER", cls="text-sm font-heading font-bold text-[#D4AF37] uppercase mb-3"),
            Form(
                Input(type="text", name="title", placeholder="Showcase / Cypher Episode Title *", required=True, cls="input-dark w-full text-xs mb-3 font-body"),
                Input(type="text", name="youtube_url", placeholder="Paste YouTube URL or 11-char ID (e.g. https://youtu.be/dQw4w9WgXcQ) *", required=True, cls="input-dark w-full text-xs mb-3 font-mono"),
                Textarea(name="description", placeholder="Short Description / Performer Lineup...", rows="2", cls="input-dark w-full text-xs mb-4 font-body"),
                Button("SAVE & PUBLISH SHOWCASE", type="submit", cls="btn-gold py-2.5 px-5 text-xs font-heading font-black cursor-pointer"),
                action="/admin/showcases/add",
                method="POST"
            ),
            cls="bg-[#121212] border border-[#222222] p-6 rounded-xl mb-8"
        ),
        Div(
            *[
                Div(
                    H4(sc["title"], cls="font-heading font-bold text-sm text-white mb-1"),
                    Span(f"ID: {sc['youtube_id']}", cls="text-[11px] font-mono text-[#D4AF37] block mb-2"),
                    P(sc.get("description", ""), cls="text-neutral-400 text-xs mb-3"),
                    Iframe(src=f"https://www.youtube.com/embed/{sc['youtube_id']}" if "videoseries" in sc['youtube_id'] else f"https://www.youtube.com/embed/{sc['youtube_id']}?rel=0", cls="w-full max-w-sm aspect-video rounded-lg"),
                    cls="p-4 bg-[#141414] border border-[#262626] rounded-xl"
                )
                for sc in showcases
            ],
            cls="grid grid-cols-1 md:grid-cols-2 gap-4"
        )
    )

    # 3. Events Tab Content (Super Admin Only)
    events_content = Div(
        Div(
            H3("ADD RAP FUNXTION EVENT", cls="text-sm font-heading font-bold text-[#D4AF37] uppercase mb-3"),
            Form(
                Input(type="text", name="title", placeholder="Event Title (e.g. Rap Funxtion 17) *", required=True, cls="input-dark w-full text-xs mb-3 font-body"),
                Input(type="text", name="date", placeholder="Date / Timeline (e.g. November 2026) *", required=True, cls="input-dark w-full text-xs mb-3 font-body"),
                Input(type="text", name="status", placeholder="Status (e.g. Tickets Live, Rescheduling) *", value="Active", cls="input-dark w-full text-xs mb-3 font-body"),
                Input(type="text", name="flyer_url", placeholder="Flyer Image Path (e.g. /static/assets/rf16_flyer_new.jpg)", value="/static/assets/rf16_flyer_new.jpg", cls="input-dark w-full text-xs mb-3 font-mono"),
                Input(type="text", name="ticket_url", placeholder="Ticket / RSVP Link", value="#", cls="input-dark w-full text-xs mb-3 font-body"),
                Textarea(name="description", placeholder="Event description...", rows="2", cls="input-dark w-full text-xs mb-4 font-body"),
                Button("PUBLISH EVENT", type="submit", cls="btn-gold py-2.5 px-5 text-xs font-heading font-black cursor-pointer"),
                action="/admin/events/add",
                method="POST"
            ),
            cls="bg-[#121212] border border-[#222222] p-6 rounded-xl mb-8"
        ),
        Div(
            *[
                Div(
                    Div(
                        Div(
                            H4(ev["title"], cls="font-heading font-bold text-base text-white mb-1"),
                            Span(f"Date: {ev.get('date')} • Status: {ev.get('status')}", cls="text-xs text-[#D4AF37] block mb-2"),
                            P(ev.get("description", ""), cls="text-neutral-400 text-xs mb-3 leading-relaxed"),
                            Img(src=ev.get("flyer_url"), cls="w-36 rounded-lg border border-[#333333] shadow-md mb-2") if ev.get("flyer_url") else None,
                            cls="flex-grow"
                        ),
                        Form(
                            Input(type="hidden", name="event_id", value=ev["id"]),
                            Button("🗑️ Delete Event", type="submit", cls="text-[10px] bg-red-950 text-red-300 border border-red-800 hover:bg-red-800 hover:text-white px-3 py-1.5 rounded cursor-pointer font-bold transition-all"),
                            action="/admin/events/delete",
                            method="POST",
                            cls="mt-2 md:mt-0"
                        ),
                        cls="flex flex-col md:flex-row justify-between items-start md:items-center"
                    ),
                    cls="p-4 bg-[#141414] border border-[#262626] rounded-xl"
                )
                for ev in events
            ],
            cls="space-y-4"
        )
    )

    # 4. Subscribers Tab Content (Super Admin Only)
    subscribers_content = Div(
        Div(
            Span(f"TOTAL SUBSCRIBERS: {len(subscribers)}", cls="text-xs font-mono font-bold text-[#D4AF37] tracking-wider uppercase block mb-4"),
            Div(
                *[
                    Div(
                        Span(sub.get("email", ""), cls="text-sm font-body text-white font-semibold"),
                        Span(sub.get("created_at", "Recently")[:10], cls="text-xs font-mono text-neutral-500"),
                        cls="p-3 bg-[#141414] border border-[#222222] rounded-lg flex justify-between items-center"
                    )
                    for sub in subscribers
                ],
                cls="space-y-2 max-h-[500px] overflow-y-auto"
            ),
            cls="p-6 bg-[#121212] border border-[#222222] rounded-xl"
        )
    )

    # 5. User Accounts Tab Content (Super Admin Only)
    artist_slug_options = [Option(a["name"], value=a["slug"]) for a in ROSTER_ARTISTS]
    users_content = Div(
        Div(
            H3("CREATE USER / ARTIST ADMIN ACCOUNT", cls="text-sm font-heading font-bold text-[#D4AF37] uppercase mb-3"),
            Form(
                Div(
                    Label("EMAIL ADDRESS:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="email", name="email", placeholder="artist@ubh.com", required=True, cls="input-dark w-full text-xs"),
                    cls="mb-3"
                ),
                Div(
                    Label("PASSWORD:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Input(type="password", name="password", placeholder="Account password...", required=True, cls="input-dark w-full text-xs font-mono"),
                    cls="mb-3"
                ),
                Div(
                    Label("ACCOUNT ROLE:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Select(
                        Option("Artist Admin (Restricted to artist slug)", value="artist_admin"),
                        Option("Super Admin (Full CMS Access)", value="super_admin"),
                        name="role",
                        cls="input-dark w-full text-xs"
                    ),
                    cls="mb-3"
                ),
                Div(
                    Label("ASSIGNED ARTIST ROSTER SLUG (FOR ARTIST ADMINS):", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Select(
                        *artist_slug_options,
                        name="artist_slug",
                        cls="input-dark w-full text-xs"
                    ),
                    cls="mb-4"
                ),
                Button("CREATE USER ACCOUNT", type="submit", cls="btn-gold py-2.5 px-6 text-xs font-heading font-black cursor-pointer"),
                action="/admin/users/create",
                method="POST"
            ),
            cls="bg-[#121212] border border-[#222222] p-6 rounded-xl mb-8"
        ),
        Div(
            Span(f"REGISTERED USER ACCOUNTS: {len(user_accounts)}", cls="text-xs font-mono font-bold text-[#D4AF37] tracking-wider uppercase block mb-4"),
            Div(
                *[
                    Div(
                        Div(
                            Span(u.get("email", ""), cls="text-sm font-body text-white font-semibold block"),
                            Span(f"Role: {u.get('role', '').upper()}" + (f" • Slug: {u.get('artist_slug')}" if u.get('artist_slug') else ""), cls="text-xs font-mono text-[#D4AF37]"),
                            cls="flex-grow"
                        ),
                        Span(u.get("created_at", "Recently")[:10], cls="text-xs font-mono text-neutral-500"),
                        cls="p-3 bg-[#141414] border border-[#222222] rounded-lg flex justify-between items-center"
                    )
                    for u in user_accounts
                ],
                cls="space-y-2 max-h-[500px] overflow-y-auto"
            ),
            cls="p-6 bg-[#121212] border border-[#222222] rounded-xl"
        )
    )

    # 6. Artist Posts Tab Content (Super Admin & Artist Admin)
    portal_heading = f"ARTIST PORTAL ({assigned_slug.upper()})" if role == "artist_admin" else "ARTIST CREATOR PORTAL"
    portal_desc = f"Publish journal dispatches and news updates directly to your official profile (/roster/{assigned_slug})." if role == "artist_admin" else "Publish posts to any artist's dedicated profile page (/roster/{slug})."

    posts_content = Div(
        Div(
            Div(
                Span("✏️", cls="text-lg mr-2"),
                H3(portal_heading, cls="text-sm font-heading font-bold text-[#D4AF37] uppercase inline"),
                cls="flex items-center mb-1"
            ),
            P(portal_desc, cls="text-neutral-500 text-[10px] mb-4"),
            Form(
                Div(
                    Label("ARTIST:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Select(
                        *artist_slug_options,
                        name="artist_slug",
                        required=True,
                        cls="input-dark w-full text-xs py-2"
                    ),
                    cls="mb-3"
                ) if role == "super_admin" else Input(type="hidden", name="artist_slug", value=assigned_slug),
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
            Span(f"PUBLISHED POSTS: {len(all_posts)}", cls="text-xs font-mono font-bold text-[#D4AF37] tracking-wider uppercase block mb-4"),
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

    tab_map = {
        'slots': slots_content,
        'showcases': showcases_content,
        'events': events_content,
        'posts': posts_content,
        'subscribers': subscribers_content,
        'users': users_content
    }
    active_tab_content = tab_map.get(tab, posts_content if role == "artist_admin" else slots_content)

    dashboard = Div(
        Div(
            # Header
            Div(
                Div(
                    Span("⚡ UBH EXECUTIVE CONSOLE", cls="text-xs font-mono text-[#D4AF37] tracking-[0.3em] font-bold block mb-1"),
                    H1("ADMIN CMS ENGINE", cls="font-heading text-3xl sm:text-4xl font-black text-white uppercase"),
                    Span(f"Active Session: {role.upper()}" + (f" ({assigned_slug})" if assigned_slug else ""), cls="text-xs font-mono text-neutral-400 block mt-1"),
                    cls="flex-grow"
                ),
                Div(
                    A("LOGOUT", href="/admin/logout", cls="btn-gold-outline text-xs py-1.5 px-4 font-heading mr-2"),
                    A("EXIT ADMIN", href="/", cls="btn-gold-outline text-xs py-1.5 px-4 font-heading"),
                    cls="flex items-center"
                ),
                cls="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 border-b border-[#1A1A1A] pb-6"
            ),
            # Messages
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
async def post_admin_slot_add_custom(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    date = str(form.get("date", "")).strip()
    time_label = str(form.get("time_label", "")).strip()
    try:
        duration = int(form.get("duration", "2"))
    except ValueError:
        duration = 2
    try:
        price = int(form.get("price", "100"))
    except ValueError:
        price = 100

    if date and time_label:
        add_custom_slot_for_date(date_str=date, time_label=time_label, duration=duration, price=price)
        return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Custom+slot+added+successfully", status_code=303)
    return RedirectResponse("/admin?tab=slots&error=Date+and+time+label+are+required", status_code=303)

@rt("/admin/slots/wipe-day")
async def post_admin_slot_wipe_day(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    date = str(form.get("date", "")).strip()
    if date:
        delete_all_slots_for_date(date)
        return RedirectResponse(f"/admin?tab=slots&date={date}&msg=All+slots+wiped+for+{date}", status_code=303)
    return RedirectResponse("/admin?tab=slots&error=Date+is+required", status_code=303)

@rt("/admin/slots/block-day")
async def post_admin_slot_block_day(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    date = str(form.get("date", "")).strip()
    if date:
        block_entire_day_for_date(date)
        return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Entire+day+blocked+for+{date}", status_code=303)
    return RedirectResponse("/admin?tab=slots&error=Date+is+required", status_code=303)

@rt("/admin/slots/update")
async def post_admin_slot_update(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    slot_id = sanitize_identifier(str(form.get("slot_id", "")))
    status = str(form.get("status", "available")).strip().lower()
    date = str(form.get("date", "")).strip()

    if not slot_id or status not in ("available", "booked", "blocked", "maintenance"):
        return RedirectResponse("/admin?tab=slots&error=Invalid+slot+parameters", status_code=303)

    slot = get_slot_by_id(slot_id)
    if not slot:
        return RedirectResponse("/admin?tab=slots&error=Slot+not+found", status_code=303)

    update_slot_status(slot_id, status)
    return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Slot+status+updated+to+{status}", status_code=303)

@rt("/admin/slots/delete")
async def post_admin_slot_delete(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    slot_id = sanitize_identifier(str(form.get("slot_id", "")))
    date = str(form.get("date", "")).strip()

    if not slot_id:
        return RedirectResponse("/admin?tab=slots&error=Invalid+slot+ID", status_code=303)

    slot = get_slot_by_id(slot_id)
    if not slot:
        return RedirectResponse("/admin?tab=slots&error=Slot+not+found", status_code=303)

    reset_slot_booking(slot_id)
    return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Booking+deleted+and+slot+re-opened+for+booking", status_code=303)

@rt("/admin/users/create")
async def post_admin_user_create(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", "")).strip()
    role = str(form.get("role", "artist_admin")).strip()
    artist_slug = str(form.get("artist_slug", "")).strip()

    if email and password:
        create_user_account(email=email, password=password, role=role, artist_slug=artist_slug)
        return RedirectResponse(f"/admin?tab=users&msg=User+account+created+for+{email}", status_code=303)

    return RedirectResponse("/admin?tab=users&error=Email+and+password+are+required", status_code=303)

@rt("/admin/showcases/add")
async def post_admin_showcase_add(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    title = str(form.get("title", "")).strip()
    youtube_url = str(form.get("youtube_url", "")).strip()
    description = str(form.get("description", "")).strip()

    if not title or not youtube_url:
        return RedirectResponse("/admin?tab=showcases&error=Title+and+YouTube+URL+are+required", status_code=303)

    yt_id, is_playlist = extract_youtube_id(youtube_url)
    if not yt_id:
        return RedirectResponse("/admin?tab=showcases&error=Invalid+YouTube+URL+or+ID", status_code=303)

    add_showcase(title=title, youtube_id=yt_id, description=description, is_playlist=is_playlist)
    return RedirectResponse("/admin?tab=showcases&msg=Showcase+published+successfully", status_code=303)

@rt("/admin/events/add")
async def post_admin_event_add(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    title = str(form.get("title", "")).strip()
    date = str(form.get("date", "")).strip()
    status = str(form.get("status", "Active")).strip()
    flyer_url = sanitize_media_url(str(form.get("flyer_url", "")), allow_relative=True)
    ticket_url = sanitize_media_url(str(form.get("ticket_url", "")), allow_relative=True, allow_hash=True)
    description = str(form.get("description", "")).strip()

    if not title or not date:
        return RedirectResponse("/admin?tab=events&error=Event+title+and+date+are+required", status_code=303)

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
async def post_admin_event_delete(req: Request):
    if not is_super_admin(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    event_id = sanitize_identifier(str(form.get("event_id", "")))

    if not event_id:
        return RedirectResponse("/admin?tab=events&error=Invalid+event+ID", status_code=303)

    events = get_events()
    if not any(ev.get("id") == event_id for ev in events):
        return RedirectResponse("/admin?tab=events&error=Event+not+found", status_code=303)

    delete_event(event_id)
    return RedirectResponse("/admin?tab=events&msg=Event+deleted+successfully", status_code=303)

@rt("/admin/posts/add")
async def post_admin_artist_post(req: Request):
    session = get_current_user_session(req)
    if not session:
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    role = session.get("role", "artist_admin")
    assigned_slug = session.get("artist_slug", "")

    if role == "artist_admin":
        artist_slug = assigned_slug
    else:
        artist_slug = sanitize_identifier(str(form.get("artist_slug", "")))

    title = str(form.get("title", "")).strip()
    body = str(form.get("body", "")).strip()
    media_url = sanitize_media_url(str(form.get("media_url", "")), allow_relative=True)

    if not artist_slug or not title or not body:
        return RedirectResponse("/admin?tab=posts&error=Title+and+body+are+required", status_code=303)

    if not any(a["slug"] == artist_slug for a in ROSTER_ARTISTS):
        return RedirectResponse("/admin?tab=posts&error=Invalid+artist+selection", status_code=303)

    add_artist_post(artist_slug=artist_slug, title=title, body=body, media_url=media_url)
    return RedirectResponse(f"/admin?tab=posts&msg=Post+published+for+{artist_slug}", status_code=303)

@rt("/admin/posts/delete")
async def post_admin_artist_post_delete(req: Request):
    session = get_current_user_session(req)
    if not session:
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    post_id = sanitize_identifier(str(form.get("post_id", "")))
    role = session.get("role", "artist_admin")
    assigned_slug = session.get("artist_slug", "")

    if not post_id:
        return RedirectResponse("/admin?tab=posts&error=Invalid+post+ID", status_code=303)

    if role == "artist_admin":
        all_posts = get_artist_posts(assigned_slug)
        if not any(p.get("id") == post_id for p in all_posts):
            return RedirectResponse("/admin?tab=posts&error=Unauthorized+to+delete+this+post", status_code=303)
        delete_artist_post(post_id)
    else:
        all_posts = get_all_artist_posts()
        if not any(p.get("id") == post_id for p in all_posts):
            return RedirectResponse("/admin?tab=posts&error=Post+not+found", status_code=303)
        delete_artist_post(post_id)

    return RedirectResponse("/admin?tab=posts&msg=Post+deleted+successfully", status_code=303)
