from fasthtml.common import *
from starlette.responses import RedirectResponse, JSONResponse
import re
import hmac
import secrets
import datetime
from typing import Optional, Union

from components.base import Layout
from components.roster import ROSTER_ARTISTS
from config import ADMIN_SECRET_KEY, ADMIN_KEY
from services.firebase_service import (
    get_all_slots_for_date_admin,
    update_slot_status,
    reset_slot_booking,
    get_events,
    add_event,
    delete_event,
    get_showcases,
    add_showcase,
    get_subscribers,
    get_all_artist_posts,
    add_artist_post,
    delete_artist_post
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
    """
    Extracts 11-character YouTube video ID or playlist ID from pasted URL.
    Returns (extracted_id, is_playlist).
    """
    raw = url_or_id.strip()
    if not raw:
        return "", False

    # Check playlist
    if "list=" in raw:
        pl_match = PLAYLIST_REGEX.search(raw)
        if pl_match:
            return f"videoseries?list={pl_match.group(1)}", True

    # Check 11-char match via URL regex
    match = YOUTUBE_REGEX.search(raw)
    if match:
        return match.group(1), False

    # If raw string is already a valid 11-char ID
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

# ----------------- Admin Authentication Helpers -----------------

def is_admin_authenticated(req) -> bool:
    """
    Verify admin authentication via:
    1. HTTP-only session cookie 'ubh_admin_session' (primary)
    2. Fallback query parameter or authorization header (for legacy/automated testing)
    Uses constant-time comparison to prevent timing attacks.
    """
    # 1. Cookie check
    session_cookie = req.cookies.get("ubh_admin_session", "")
    if session_cookie and hmac.compare_digest(session_cookie, ADMIN_KEY):
        return True

    # 2. Query param or header fallback
    key_param = req.query_params.get("key", "")
    if key_param and hmac.compare_digest(key_param, ADMIN_KEY):
        return True

    auth_header = req.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if hmac.compare_digest(token, ADMIN_KEY):
            return True

    return False

# ----------------- Admin Routes -----------------

@rt("/admin/login")
async def post_admin_login(req):
    """Handle admin authentication form submission and set HTTP-only session cookie."""
    form = await req.form()
    key = form.get("key", "").strip()
    
    if key and hmac.compare_digest(key, ADMIN_KEY):
        resp = RedirectResponse("/admin?msg=Authenticated+successfully", status_code=303)
        resp.set_cookie(
            key="ubh_admin_session",
            value=ADMIN_KEY,
            httponly=True,
            samesite="lax",
            secure=False  # Set True in strict HTTPS environments
        )
        return resp

    return RedirectResponse("/admin?error=Invalid+admin+security+key", status_code=303)

@rt("/admin/logout")
def get_admin_logout():
    """Clear admin session cookie and redirect to login."""
    resp = RedirectResponse("/admin?msg=Logged+out+successfully", status_code=303)
    resp.delete_cookie("ubh_admin_session")
    return resp

@rt("/admin")
def get_admin(req, date: str = "", tab: str = "slots", msg: str = "", error: str = ""):
    # PRE-QUERY AUTH CHECK: Verify session BEFORE querying any backend collections!
    if not is_admin_authenticated(req):
        # Render Login Form without exposing sensitive data or performing database queries
        login_view = Div(
            Div(
                Span("🔒 ACCESS RESTRICTED", cls="text-xs font-mono text-[#D4AF37] tracking-[0.3em] block mb-2 font-bold"),
                H2("UBH CMS PORTAL", cls="font-heading text-3xl font-black text-white uppercase mb-4"),
                P("Enter the master administrative key to access the scheduling console and content engine.", cls="text-neutral-400 text-xs md:text-sm mb-6"),
                Div(
                    P(f"❌ {error}", cls="text-rose-400 text-xs font-bold text-center"),
                    cls="mb-6 p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl"
                ) if error else None,
                Div(
                    P(f"✓ {msg}", cls="text-emerald-400 text-xs font-bold text-center"),
                    cls="mb-6 p-3 bg-emerald-950/40 border border-emerald-800/60 rounded-xl"
                ) if msg else None,
                Form(
                    Input(
                        type="password",
                        name="key",
                        placeholder="ENTER ADMIN SECURITY KEY",
                        required=True,
                        cls="input-dark w-full text-center tracking-widest text-sm mb-4 font-mono"
                    ),
                    Button(
                        "AUTHENTICATE",
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

    # User IS authenticated -> Load CMS data safely
    if not date:
        date = datetime.date.today().isoformat()

    slots = get_all_slots_for_date_admin(date)
    events = get_events()
    showcases = get_showcases()
    subscribers = get_subscribers()
    all_posts = get_all_artist_posts()

    # Nav Tabs (Clean URLs without key in query string!)
    tabs_header = Div(
        A(f"📅 Studio Slots ({date})", href=f"/admin?tab=slots&date={date}", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'slots' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        A(f"🎥 YouTube Showcases ({len(showcases)})", href=f"/admin?tab=showcases", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'showcases' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        A(f"🎤 Rap Funxtion Events ({len(events)})", href=f"/admin?tab=events", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'events' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        A(f"✏️ Artist Posts ({len(all_posts)})", href=f"/admin?tab=posts", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'posts' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        A(f"✉️ Subscribers ({len(subscribers)})", href=f"/admin?tab=subscribers", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'subscribers' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        cls="flex flex-wrap gap-2 mb-8"
    )

    # 1. Slots Tab Content
    slots_content = Div(
        # Date selector
        Form(
            Label("SELECT DATE TO VIEW & MANAGE SLOTS:", cls="text-xs font-heading font-bold text-neutral-400 uppercase block mb-2"),
            Div(
                Input(type="date", name="date", value=date, cls="input-dark text-xs py-2 px-3 font-mono"),
                Input(type="hidden", name="tab", value="slots"),
                Button("LOAD DATE", type="submit", cls="btn-gold py-2 px-4 text-xs font-heading font-bold cursor-pointer"),
                cls="flex gap-2 items-center"
            ),
            action="/admin",
            method="GET",
            cls="mb-6 p-4 bg-[#121212] border border-[#222222] rounded-xl"
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
                    ) if slot.get("status") == "booked" else P("Slot is open for public booking.", cls="text-xs text-neutral-500 italic mb-4"),
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
            ],
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        )
    )

    # 2. Showcases Tab Content
    showcases_content = Div(
        # Add Showcase Form
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
        # Existing Showcases List
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

    # 3. Events Tab Content
    events_content = Div(
        # Add Event Form
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
        # Existing Events
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

    # 4. Posts Tab Content
    artist_slug_options = [
        Option(f"{art['name']} ({art['slug']})", value=art['slug'])
        for art in ROSTER_ARTISTS
    ]

    posts_content = Div(
        # Create Post Form
        Div(
            H3("PUBLISH ARTIST POST / DISPATCH", cls="font-heading font-bold text-sm text-[#D4AF37] uppercase mb-4"),
            Form(
                Div(
                    Label("SELECT ARTIST:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
                    Select(
                        *artist_slug_options,
                        name="artist_slug",
                        required=True,
                        cls="input-dark w-full text-xs py-2"
                    ),
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
        # Existing posts
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

    # 5. Subscribers Tab Content
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

    # Choose active tab
    tab_map = {
        'slots': slots_content,
        'showcases': showcases_content,
        'events': events_content,
        'posts': posts_content,
        'subscribers': subscribers_content
    }
    active_tab_content = tab_map.get(tab, slots_content)

    dashboard = Div(
        Div(
            # Header
            Div(
                Div(
                    Span("⚡ UBH EXECUTIVE CONSOLE", cls="text-xs font-mono text-[#D4AF37] tracking-[0.3em] font-bold block mb-1"),
                    H1("ADMIN CMS ENGINE", cls="font-heading text-3xl sm:text-4xl font-black text-white uppercase"),
                    cls="flex-grow"
                ),
                A("LOG OUT", href="/admin/logout", cls="btn-gold-outline text-xs py-1.5 px-4 font-heading"),
                cls="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 border-b border-[#1A1A1A] pb-6"
            ),
            # Message banner
            Div(
                P(f"✓ {msg}", cls="text-emerald-400 text-xs font-bold text-center"),
                cls="mb-6 p-3 bg-emerald-950/40 border border-emerald-800/60 rounded-xl"
            ) if msg else None,
            tabs_header,
            active_tab_content,
            cls="max-w-6xl mx-auto px-6 py-10"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Admin CMS Engine", dashboard, show_nav=True, show_footer=True, show_capture=False)

# ----------------- Admin Action Handlers -----------------

@rt("/admin/slots/update")
async def post_admin_slot_update(req):
    if not is_admin_authenticated(req):
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
    """Delete a customer booking and reset the slot back to available."""
    if not is_admin_authenticated(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    slot_id = sanitize_resource_id(form.get("slot_id", ""))
    date = form.get("date", "").strip()

    if slot_id:
        reset_slot_booking(slot_id)
    return RedirectResponse(f"/admin?tab=slots&date={date}&msg=Booking+deleted+and+slot+re-opened+for+booking", status_code=303)

@rt("/admin/slots/reset")
async def post_admin_slot_reset(req):
    """Reset a slot back to available (alias for delete)."""
    return await post_admin_slot_delete(req)

@rt("/admin/showcases/add")
async def post_admin_showcase_add(req):
    if not is_admin_authenticated(req):
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
    if not is_admin_authenticated(req):
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
    """Delete an event from the roster and update admin view."""
    if not is_admin_authenticated(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    event_id = sanitize_resource_id(form.get("event_id", ""))

    if event_id:
        delete_event(event_id)
    return RedirectResponse("/admin?tab=events&msg=Event+deleted+successfully", status_code=303)

@rt("/admin/posts/add")
async def post_admin_artist_post(req):
    """Handle artist post creation from the Creator Portal."""
    if not is_admin_authenticated(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
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
    """Handle artist post deletion from the CMS."""
    if not is_admin_authenticated(req):
        return RedirectResponse("/admin?error=Unauthorized", status_code=303)

    form = await req.form()
    post_id = sanitize_resource_id(form.get("post_id", ""))

    if post_id:
        delete_artist_post(post_id)

    return RedirectResponse("/admin?tab=posts&msg=Post+deleted+successfully", status_code=303)
