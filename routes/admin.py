from fasthtml.common import *
from starlette.responses import RedirectResponse, JSONResponse
import re
import datetime
from typing import Optional

from components.base import Layout
from components.roster import ROSTER_ARTISTS
from config import ADMIN_KEY
from services.firebase_service import (
    get_all_slots_for_date_admin,
    update_slot_status,
    get_events,
    add_event,
    get_showcases,
    add_showcase,
    get_subscribers,
    get_all_artist_posts,
    add_artist_post
)

admin_app = FastHTML()
rt = admin_app.route

# ----------------- YouTube ID Regex Extractor -----------------
YOUTUBE_REGEX = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?|shorts)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
    re.IGNORECASE
)
PLAYLIST_REGEX = re.compile(r'[?&]list=([a-zA-Z0-9_-]+)', re.IGNORECASE)

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

    # If raw string is already an 11-char ID
    if len(raw) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', raw):
        return raw, False

    return raw, False

# ----------------- Admin Routes -----------------

@rt("/admin")
def get_admin(key: str = "", date: str = "", tab: str = "slots", msg: str = ""):
    # Check simple auth
    is_authenticated = (key == ADMIN_KEY)
    
    if not is_authenticated:
        # Render Login Form
        login_view = Div(
            Div(
                Span("🔒 ACCESS RESTRICTED", cls="text-xs font-mono text-[#D4AF37] tracking-[0.3em] block mb-2 font-bold"),
                H2("UBH CMS PORTAL", cls="font-heading text-3xl font-black text-white uppercase mb-4"),
                P("Enter the master administrative key to access the scheduling console and content engine.", cls="text-neutral-400 text-xs md:text-sm mb-6"),
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
                    action="/admin",
                    method="GET"
                ),
                cls="bg-[#0D0D0D] border border-[#1F1F1F] rounded-2xl p-8 md:p-10 shadow-2xl max-w-md mx-auto text-center"
            ),
            cls="max-w-3xl mx-auto px-6 py-20"
        )
        return Layout("Admin Login", login_view, show_nav=True, show_footer=True, show_capture=False)

    # If authenticated, load CMS data
    if not date:
        date = datetime.date.today().isoformat()

    slots = get_all_slots_for_date_admin(date)
    events = get_events()
    showcases = get_showcases()
    subscribers = get_subscribers()
    all_posts = get_all_artist_posts()

    # Nav Tabs
    tabs_header = Div(
        A(f"📅 Studio Slots ({date})", href=f"/admin?key={key}&tab=slots&date={date}", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'slots' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        A(f"🎥 YouTube Showcases ({len(showcases)})", href=f"/admin?key={key}&tab=showcases", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'showcases' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        A(f"🎤 Rap Funxtion Events ({len(events)})", href=f"/admin?key={key}&tab=events", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'events' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        A(f"✏️ Artist Posts ({len(all_posts)})", href=f"/admin?key={key}&tab=posts", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'posts' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        A(f"✉️ Subscribers ({len(subscribers)})", href=f"/admin?key={key}&tab=subscribers", cls=f"px-4 py-2.5 rounded-lg text-xs font-heading font-bold uppercase transition-all { 'bg-[#D4AF37] text-black' if tab == 'subscribers' else 'bg-[#141414] text-neutral-400 hover:text-white' }"),
        cls="flex flex-wrap gap-2 mb-8"
    )

    # 1. Slots Tab Content
    slots_content = Div(
        # Date selector
        Form(
            Input(type="hidden", name="key", value=key),
            Input(type="hidden", name="tab", value="slots"),
            Div(
                Label("INSPECT DATE:", cls="text-xs font-heading font-bold text-neutral-400 uppercase mr-3"),
                Input(
                    type="date",
                    name="date",
                    value=date,
                    onchange="this.form.submit()",
                    cls="input-dark text-xs py-1.5 px-3"
                ),
                Button("UPDATE VIEW", type="submit", cls="btn-gold-outline text-[10px] py-1 px-3 ml-2"),
                cls="flex items-center"
            ),
            method="GET",
            action="/admin",
            cls="mb-6 p-4 bg-[#121212] border border-[#222222] rounded-xl flex items-center justify-between"
        ),
        # Slots Grid
        Div(
            *[
                Div(
                    Div(
                        Span(slot["time_label"], cls="font-heading font-bold text-sm text-white block"),
                        Span(f"${slot.get('price', 100)} USD • Status: ", cls="text-xs text-neutral-400"),
                        Span(
                            slot.get("status", "available").upper(),
                            cls=f"text-xs font-mono font-bold { 'text-emerald-400' if slot.get('status') == 'available' else 'text-amber-400' if slot.get('status') == 'booked' else 'text-rose-400' }"
                        ),
                        P(f"Artist: {slot.get('artist_name')} ({slot.get('artist_email')})", cls="text-xs text-[#D4AF37] mt-1") if slot.get("artist_name") else None,
                        cls="flex-grow"
                    ),
                    # Action buttons to change status
                    Div(
                        Form(
                            Input(type="hidden", name="key", value=key),
                            Input(type="hidden", name="slot_id", value=slot["id"]),
                            Input(type="hidden", name="status", value="available"),
                            Input(type="hidden", name="date", value=date),
                            Button("Set Available", type="submit", cls="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 hover:bg-emerald-800 hover:text-white px-2.5 py-1 rounded cursor-pointer"),
                            action="/admin/slots/update",
                            method="POST"
                        ),
                        Form(
                            Input(type="hidden", name="key", value=key),
                            Input(type="hidden", name="slot_id", value=slot["id"]),
                            Input(type="hidden", name="status", value="booked"),
                            Input(type="hidden", name="date", value=date),
                            Button("Set Booked", type="submit", cls="text-[10px] bg-amber-950 text-amber-300 border border-amber-800 hover:bg-amber-800 hover:text-white px-2.5 py-1 rounded cursor-pointer"),
                            action="/admin/slots/update",
                            method="POST"
                        ),
                        Form(
                            Input(type="hidden", name="key", value=key),
                            Input(type="hidden", name="slot_id", value=slot["id"]),
                            Input(type="hidden", name="status", value="blocked"),
                            Input(type="hidden", name="date", value=date),
                            Button("Block Slot", type="submit", cls="text-[10px] bg-rose-950 text-rose-300 border border-rose-800 hover:bg-rose-800 hover:text-white px-2.5 py-1 rounded cursor-pointer"),
                            action="/admin/slots/update",
                            method="POST"
                        ),
                        cls="flex gap-2 flex-wrap items-center mt-3 md:mt-0"
                    ),
                    cls="p-4 bg-[#141414] border border-[#262626] rounded-xl flex flex-col md:flex-row justify-between items-start md:items-center"
                )
                for slot in slots
            ],
            cls="space-y-3"
        )
    )

    # 2. Showcases Tab Content
    showcases_content = Div(
        # Form to add new showcase
        Div(
            H3("ADD YOUTUBE SHOWCASE / CYPHER", cls="text-sm font-heading font-bold text-[#D4AF37] uppercase mb-3"),
            Form(
                Input(type="hidden", name="key", value=key),
                Input(type="text", name="title", placeholder="Showcase / Cypher Episode Title *", required=True, cls="input-dark w-full text-xs mb-3 font-body"),
                Input(type="text", name="youtube_url", placeholder="Paste YouTube URL or 11-char ID (e.g. https://youtu.be/dQw4w9WgXcQ) *", required=True, cls="input-dark w-full text-xs mb-3 font-mono"),
                Textarea(name="description", placeholder="Short Description / Performer Lineup...", rows="2", cls="input-dark w-full text-xs mb-4 font-body"),
                Button("SAVE & PUBLISH SHOWCASE", type="submit", cls="btn-gold py-2.5 px-5 text-xs font-heading font-black cursor-pointer"),
                action="/admin/showcases/add",
                method="POST"
            ),
            cls="bg-[#121212] border border-[#222222] p-6 rounded-xl mb-8"
        ),
        # Existing showcases
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

    # 3. Events Tab Content
    events_content = Div(
        Div(
            H3("ADD RAP FUNXTION EVENT", cls="text-sm font-heading font-bold text-[#D4AF37] uppercase mb-3"),
            Form(
                Input(type="hidden", name="key", value=key),
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
                    H4(ev["title"], cls="font-heading font-bold text-base text-white mb-1"),
                    Span(f"Date: {ev.get('date')} • Status: {ev.get('status')}", cls="text-xs text-[#D4AF37] block mb-2"),
                    P(ev.get("description", ""), cls="text-neutral-400 text-xs mb-3"),
                    Img(src=ev.get("flyer_url"), cls="w-36 rounded-lg border border-[#333333] shadow-md") if ev.get("flyer_url") else None,
                    cls="p-4 bg-[#141414] border border-[#262626] rounded-xl"
                )
                for ev in events
            ],
            cls="space-y-4"
        )
    )

    # 4. Subscribers Tab Content
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

    # 5. Artist Posts Tab Content (Creator Portal)
    artist_slug_options = [Option(a["name"], value=a["slug"]) for a in ROSTER_ARTISTS]
    posts_content = Div(
        # Publish New Post Form
        Div(
            Div(
                Span("✏️", cls="text-lg mr-2"),
                H3("ARTIST CREATOR PORTAL", cls="text-sm font-heading font-bold text-[#D4AF37] uppercase inline"),
                cls="flex items-center mb-1"
            ),
            P("Publish posts to an artist's dedicated profile page. Posts appear instantly on /roster/{slug}.", cls="text-neutral-500 text-[10px] mb-4"),
            Form(
                Input(type="hidden", name="key", value=key),
                Div(
                    Label("ARTIST:", cls="text-[10px] font-heading font-bold text-neutral-400 uppercase block mb-1.5"),
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
                        P(p.get('body', '')[:120] + ('...' if len(p.get('body', '')) > 120 else ''), cls="text-neutral-400 text-xs mb-2"),
                        A(f"View on profile →", href=f"/roster/{p.get('artist_slug')}#post-{p.get('id')}", cls="text-[10px] text-[#D4AF37] hover:text-[#FFD700] font-heading font-bold tracking-wider"),
                        cls="p-4 bg-[#141414] border border-[#262626] rounded-xl"
                    )
                    for p in all_posts
                ] if all_posts else [P("No posts published yet. Use the form above to create the first one.", cls="text-neutral-500 text-xs italic")],
                cls="space-y-3 max-h-[600px] overflow-y-auto"
            ),
            cls="p-6 bg-[#121212] border border-[#222222] rounded-xl"
        )
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
                A("EXIT ADMIN", href="/", cls="btn-gold-outline text-xs py-1.5 px-4 font-heading"),
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
    form = await req.form()
    key = form.get("key", "")
    slot_id = form.get("slot_id", "")
    status = form.get("status", "available")
    date = form.get("date", "")

    if key != ADMIN_KEY:
        return RedirectResponse("/admin", status_code=303)

    update_slot_status(slot_id, status)
    return RedirectResponse(f"/admin?key={key}&tab=slots&date={date}&msg=Slot+status+updated+to+{status}", status_code=303)

@rt("/admin/showcases/add")
async def post_admin_showcase_add(req):
    form = await req.form()
    key = form.get("key", "")
    title = form.get("title", "").strip()
    youtube_url = form.get("youtube_url", "").strip()
    description = form.get("description", "").strip()

    if key != ADMIN_KEY:
        return RedirectResponse("/admin", status_code=303)

    yt_id, is_playlist = extract_youtube_id(youtube_url)
    if not yt_id:
        return RedirectResponse(f"/admin?key={key}&tab=showcases&msg=Invalid+YouTube+URL", status_code=303)

    add_showcase(title=title, youtube_id=yt_id, description=description, is_playlist=is_playlist)
    return RedirectResponse(f"/admin?key={key}&tab=showcases&msg=Showcase+published+successfully", status_code=303)

@rt("/admin/events/add")
async def post_admin_event_add(req):
    form = await req.form()
    key = form.get("key", "").strip()
    title = form.get("title", "").strip()
    date = form.get("date", "").strip()
    status = form.get("status", "Active").strip()
    flyer_url = form.get("flyer_url", "").strip()
    ticket_url = form.get("ticket_url", "").strip()
    description = form.get("description", "").strip()

    if key != ADMIN_KEY:
        return RedirectResponse("/admin", status_code=303)

    add_event(
        title=title,
        date=date,
        status=status,
        flyer_url=flyer_url,
        ticket_url=ticket_url,
        description=description
    )
    return RedirectResponse(f"/admin?key={key}&tab=events&msg=Event+added+successfully", status_code=303)

@rt("/admin/posts/add")
async def post_admin_artist_post(req):
    """Handle artist post creation from the Creator Portal."""
    form = await req.form()
    key = form.get("key", "").strip()
    artist_slug = form.get("artist_slug", "").strip()
    title = form.get("title", "").strip()
    body = form.get("body", "").strip()
    media_url = form.get("media_url", "").strip()

    if key != ADMIN_KEY:
        return RedirectResponse("/admin", status_code=303)

    if not artist_slug or not title or not body:
        return RedirectResponse(f"/admin?key={key}&tab=posts&msg=Title+and+body+are+required", status_code=303)

    add_artist_post(artist_slug=artist_slug, title=title, body=body, media_url=media_url)
    return RedirectResponse(f"/admin?key={key}&tab=posts&msg=Post+published+for+{artist_slug}", status_code=303)
