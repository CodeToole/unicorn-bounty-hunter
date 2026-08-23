from fasthtml.common import *
from starlette.responses import JSONResponse
import datetime

from components.base import Layout
from components.roster import RosterSection, get_artist_by_slug, ROSTER_ARTISTS
from components.calendar import BookingCalendar
from components.player import YouTubeShowcasePlayer, BandcampVaultPlayer
from components.artist_profile import ArtistProfilePage
from services.firebase_service import (
    get_slots_for_date,
    get_events,
    get_showcases,
    add_subscriber,
    get_artist_posts
)

public_app = FastHTML()
rt = public_app.route

# ----------------- Homepage -----------------
@rt("/")
def get_home():
    hero_section = Section(
        # Background video
        Video(
            Source(src="/static/videos/webfunxion.mp4", type="video/mp4"),
            autoplay=True,
            loop=True,
            muted=True,
            playsinline=True,
            cls="fixed inset-0 w-full h-full object-cover z-0 opacity-40 filter grayscale contrast-125"
        ),
        # Dark obsidian gradient overlay
        Div(cls="fixed inset-0 w-full h-full bg-gradient-to-b from-[#0A0A0A]/90 via-[#0A0A0A]/95 to-[#0A0A0A] z-10"),
        # Hero Foreground Content
        Div(
            # Brand Badge
            Div(
                Div(
                    Img(
                        src="/static/assets/ubh_logo.jpg",
                        alt="Unicorn Bounty Hunters Official Logo",
                        cls="w-48 sm:w-64 md:w-80 object-contain rounded-2xl shadow-2xl gold-glow-lg mx-auto mb-8 border border-[#D4AF37]/30"
                    ),
                    Span("⚡ SOUND • VISION • MASTERY", cls="text-xs tracking-[0.4em] text-[#D4AF37] font-heading font-black block mb-3 uppercase"),
                    H1(
                        "UNICORN BOUNTY HUNTERS",
                        cls="font-heading text-4xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter text-white uppercase leading-none drop-shadow-2xl mb-6"
                    ),
                    P(
                        "Independent music collective, elite recording facility, and producers of the Rap Funxtion showcase series. Uncompromising underground culture engineered with surgical precision.",
                        cls="text-neutral-300 text-sm sm:text-base md:text-lg max-w-2xl mx-auto leading-relaxed mb-10 font-body"
                    ),
                    # Action buttons
                    Div(
                        A("BOOK STUDIO TIME", href="/booking", cls="btn-gold text-xs sm:text-sm py-4 px-8 tracking-widest"),
                        A("THE VAULT", href="/music", cls="btn-gold-outline text-xs sm:text-sm py-4 px-8 tracking-widest"),
                        cls="flex flex-col sm:flex-row items-center justify-center gap-4"
                    ),
                    cls="text-center"
                ),
                cls="relative z-20 max-w-5xl mx-auto px-6 py-20 md:py-28 flex flex-col items-center justify-center min-h-[85vh]"
            ),
            cls="relative w-full z-20"
        ),
        cls="relative w-full overflow-hidden"
    )

    # Roster Section
    roster = RosterSection()

    # Showcase Teaser Section
    showcase_teaser = Section(
        Div(
            Div(
                Div(
                    Div(cls="w-16 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60"),
                    Span("ORIGINAL CONTENT", cls="font-body text-[#D4AF37] text-xs tracking-[0.4em] uppercase font-semibold"),
                    Div(cls="w-16 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60"),
                    cls="flex items-center justify-center gap-4 mb-4"
                ),
                H2("MUSICAL CHAIRS SERIES", cls="font-heading text-3xl sm:text-4xl md:text-5xl font-black tracking-tight text-white uppercase text-center mb-4"),
                P("High-octane cyphers and live underground performances captured inside the UBH sanctuary.", cls="text-neutral-400 text-sm md:text-base text-center max-w-xl mx-auto mb-10"),
                cls="max-w-7xl mx-auto px-6 text-center"
            ),
            YouTubeShowcasePlayer(
                "videoseries?list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1",
                title="UBH Musical Chairs — Official Cypher Playlist",
                description="Stream the complete official cypher playlist featuring headliners, producers, and underground innovators."
            ),
            Div(
                A("VIEW FULL SHOWCASE CATALOG", href="/showcase", cls="btn-gold-outline text-xs tracking-widest py-3 px-6 mt-8 inline-block"),
                cls="text-center"
            ),
            cls="max-w-6xl mx-auto px-6 py-16 md:py-24"
        ),
        cls="w-full relative z-20 bg-[#050505] border-t border-b border-[#1A1A1A]"
    )

    return Layout("Official Collective & Studio", hero_section, roster, showcase_teaser, current_path="/")

# ----------------- Services & Studio Booking -----------------
@rt("/services")
def get_services(error: str = "", cancelled: str = ""):
    today_str = datetime.date.today().isoformat()
    slots = get_slots_for_date(today_str)

    content = Div(
        Div(
            # Notifications / Errors
            Div(
                P(f"⚠️ {error}", cls="text-rose-400 font-bold text-sm text-center"),
                cls="mb-6 p-4 bg-rose-950/40 border border-rose-800/60 rounded-xl"
            ) if error else None,
            Div(
                P("Session booking was cancelled. Feel free to choose another date, package, or time below.", cls="text-amber-400 text-sm text-center"),
                cls="mb-6 p-4 bg-amber-950/40 border border-amber-800/60 rounded-xl"
            ) if cancelled else None,
            # Page Title
            Div(
                Span("CREATIVE FACILITY & RATES", cls="text-xs font-heading font-bold tracking-[0.4em] text-[#D4AF37] uppercase block mb-3"),
                H1("STUDIO SERVICES & BOOKING", cls="font-heading text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-white uppercase mb-4"),
                P("Professional recording, vocal production, engineering, and podcast broadcasting in our acoustic room.", cls="text-neutral-400 text-sm md:text-base max-w-2xl mx-auto leading-relaxed"),
                cls="text-center mb-12"
            ),
            # Services Grid Overview
            Div(
                Div(
                    Span("🎙️", cls="text-3xl mb-3 block"),
                    H3("STUDIO RECORDING", cls="font-heading font-bold text-xl text-white uppercase mb-2"),
                    Span("$50 / HOUR", cls="text-xs font-mono font-bold text-[#D4AF37] bg-[#141414] px-3 py-1 rounded-full border border-[#D4AF37]/30 mb-3 inline-block"),
                    P("Dedicated vocal tracking, beat production review, Pro Tools sessions, and acoustic room access with resident UBH sound engineers.", cls="text-neutral-400 text-xs md:text-sm leading-relaxed mb-4"),
                    Ul(
                        Li("✓ Slate Digital & Shure reference mics", cls="text-xs text-neutral-300"),
                        Li("✓ Real-time auto-tune & vocal chains", cls="text-xs text-neutral-300"),
                        Li("✓ Stems & raw WAV exports included", cls="text-xs text-neutral-300"),
                        cls="space-y-1.5 list-none p-0 text-left"
                    ),
                    cls="p-6 md:p-8 bg-[#0D0D0D] border border-[#1F1F1F] rounded-2xl flex flex-col"
                ),
                Div(
                    Span("📻", cls="text-3xl mb-3 block"),
                    H3("SHADOW TALK PODCAST", cls="font-heading font-bold text-xl text-white uppercase mb-2"),
                    Span("$50 / 1-HR SESSION", cls="text-xs font-mono font-bold text-[#D4AF37] bg-[#141414] px-3 py-1 rounded-full border border-[#D4AF37]/30 mb-3 inline-block"),
                    P("Host your broadcast, conduct in-depth artist interviews, or film multi-cam video podcasts with full lighting and multi-track audio capture.", cls="text-neutral-400 text-xs md:text-sm leading-relaxed mb-4"),
                    Ul(
                        Li("✓ 4-Mic broadcast setup", cls="text-xs text-neutral-300"),
                        Li("✓ 4K video recording available", cls="text-xs text-neutral-300"),
                        Li("✓ Bundle with Musical Chairs for $100", cls="text-xs text-neutral-300"),
                        cls="space-y-1.5 list-none p-0 text-left"
                    ),
                    cls="p-6 md:p-8 bg-[#0D0D0D] border border-[#1F1F1F] rounded-2xl flex flex-col"
                ),
                cls="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-16"
            ),
            # Interactive Datastar Calendar
            BookingCalendar(selected_date=today_str, slots=slots),
            cls="max-w-6xl mx-auto px-6 py-12 md:py-20"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Studio Services & Recording", content, current_path="/services")

# ----------------- Showcase & Musical Chairs -----------------
@rt("/showcase")
@rt("/musical-chairs")
def get_showcase():
    showcases = get_showcases()
    primary_showcase = showcases[0] if showcases else {
        "youtube_id": "videoseries?list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1",
        "title": "UBH Musical Chairs Cyphers",
        "description": "Official YouTube Cyphers and Live Performances."
    }

    content = Div(
        Div(
            # Header
            Div(
                Span("ORIGINAL BROADCASTS & CYPHERS", cls="text-xs font-heading font-bold tracking-[0.4em] text-[#D4AF37] uppercase block mb-3"),
                H1("MUSICAL CHAIRS SHOWCASE", cls="font-heading text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-white uppercase mb-4"),
                P("Raw verses, live production breakdowns, and underground cyphers filmed straight from the UBH studio floor.", cls="text-neutral-400 text-sm md:text-base max-w-2xl mx-auto leading-relaxed"),
                cls="text-center mb-12"
            ),
            # Primary Player
            YouTubeShowcasePlayer(
                primary_showcase.get("youtube_id", ""),
                title=primary_showcase.get("title", "Musical Chairs Cypher Series"),
                description=primary_showcase.get("description", "")
            ),
            # Showcase list
            Div(
                H3("SHOWCASE EPISODES & ARCHIVE", cls="font-heading font-bold text-xl text-white uppercase tracking-wider mb-6 text-center md:text-left"),
                Div(
                    *[
                        Div(
                            Div(
                                Iframe(
                                    src=f"https://www.youtube.com/embed/{sc['youtube_id']}" if "videoseries" in sc['youtube_id'] or "list=" in sc['youtube_id'] else f"https://www.youtube.com/embed/{sc['youtube_id']}?rel=0",
                                    allowfullscreen="true",
                                    cls="w-full aspect-video rounded-lg mb-3"
                                ),
                                H4(sc["title"], cls="font-heading font-bold text-base text-white mb-1"),
                                P(sc.get("description", ""), cls="text-neutral-400 text-xs leading-relaxed"),
                                cls="p-4 bg-[#0D0D0D] border border-[#1F1F1F] rounded-xl flex flex-col"
                            ),
                            cls="w-full"
                        )
                        for sc in showcases
                    ],
                    cls="grid grid-cols-1 md:grid-cols-2 gap-6"
                ),
                cls="mt-16 max-w-4xl mx-auto"
            ) if len(showcases) > 1 else None,
            cls="max-w-6xl mx-auto px-6 py-12 md:py-20"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Musical Chairs Showcase", content, current_path="/showcase")

# ----------------- Rap Funxtion Live Events -----------------
@rt("/rap-funxtion")
def get_rap_funxtion():
    events = get_events()
    active_event = events[0] if events else {}

    lineup = [
        {"name": "Ali Kazem", "tag": "Headliner"},
        {"name": "Tayo-Sei", "tag": "Featured"},
        {"name": "Whoistidez", "tag": "Featured"},
        {"name": "Lowkee (G.O.M)", "tag": "Featured"},
        {"name": "Unknown", "tag": "Featured"},
        {"name": "Yung Illie", "tag": "Featured"},
        {"name": "Ongopeppo", "tag": "Featured"},
        {"name": "Merro", "tag": "Featured"},
    ]

    content = Div(
        Div(
            # Header
            Div(
                Span("LIVE HIP-HOP EXPERIENCE", cls="text-xs font-heading font-bold tracking-[0.4em] text-[#D4AF37] uppercase block mb-3"),
                H1("RAP FUNXTION", cls="font-heading text-4xl sm:text-6xl md:text-7xl font-black tracking-tight text-white uppercase mb-4"),
                Div(
                    Span("STATUS: RESCHEDULING IN PROGRESS", cls="font-mono text-xs text-[#D4AF37] bg-[#1A1A1A] border border-[#D4AF37]/40 px-3 py-1.5 rounded-full inline-block mb-4 font-bold"),
                    P(
                        "The showcase date is being rescheduled. New venue configurations, date announcements, and performer additions will be delivered directly to the Hunt email roster.",
                        cls="text-neutral-400 text-sm md:text-base max-w-2xl mx-auto leading-relaxed"
                    ),
                    cls="text-center"
                ),
                cls="text-center mb-12"
            ),
            # Official Flyer Card
            Div(
                Div(
                    Img(
                        src=active_event.get("flyer_url", "/static/assets/rf16_flyer_new.jpg"),
                        alt="Rap Funxtion Official Showcase Flyer",
                        cls="w-full max-w-md rounded-2xl shadow-2xl gold-glow border border-[#D4AF37]/30 mx-auto"
                    ),
                    cls="flex justify-center mb-16"
                ),
                # The Lineup Grid
                Div(
                    Div(
                        Div(cls="w-16 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60"),
                        Span("PERFORMING LIVE", cls="font-body text-[#D4AF37] text-xs tracking-[0.4em] uppercase font-semibold"),
                        Div(cls="w-16 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60"),
                        cls="flex items-center justify-center gap-4 mb-4"
                    ),
                    H2("THE LINEUP", cls="font-heading text-3xl sm:text-4xl md:text-5xl font-black tracking-tight text-white uppercase text-center mb-10"),
                    Div(
                        *[
                            Div(
                                Div(
                                    # Monogram circle
                                    Div(
                                        Span(artist["name"][0].upper(), cls="font-heading font-black text-xl text-neutral-400 group-hover:text-[#D4AF37] transition-colors"),
                                        cls="w-16 h-16 rounded-full bg-[#111111] border border-[#222222] group-hover:border-[#D4AF37]/50 flex items-center justify-center mb-4 transition-colors"
                                    ),
                                    H3(artist["name"], cls="font-heading font-bold text-base text-[#D4AF37] uppercase mb-1"),
                                    Span(artist["tag"], cls="text-[11px] font-body text-neutral-400 uppercase tracking-widest"),
                                    cls="p-6 bg-[#0D0D0D] border border-[#1E1E1E] hover:border-[#D4AF37]/60 rounded-xl flex flex-col items-center text-center card-hover-gold"
                                ),
                                cls="group"
                            )
                            for artist in lineup
                        ],
                        cls="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4 md:gap-6"
                    ),
                    cls="max-w-5xl mx-auto mb-16"
                ),
                cls="w-full"
            ),
            cls="max-w-6xl mx-auto px-6 py-12 md:py-20"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Rap Funxtion Live Showcase", content, current_path="/rap-funxtion")

# ----------------- The Vault (Music) -----------------
@rt("/music")
def get_music():
    content = Div(
        Div(
            # Header
            Div(
                Span("OFFICIAL CATALOG & RELEASES", cls="text-xs font-heading font-bold tracking-[0.4em] text-[#D4AF37] uppercase block mb-3"),
                H1("THE VAULT", cls="font-heading text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-white uppercase mb-4"),
                P("Support the roster directly. Stream and purchase official UBH catalog releases via Bandcamp.", cls="text-neutral-400 text-sm md:text-base max-w-xl mx-auto leading-relaxed"),
                cls="text-center mb-12"
            ),
            # Embedded Bandcamp Players
            BandcampVaultPlayer(),
            cls="max-w-6xl mx-auto px-6 py-12 md:py-20"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("The Vault — Music Catalog", content, current_path="/music")

# ----------------- Merch (Apparel) -----------------
@rt("/merch")
def get_merch():
    content = Div(
        Div(
            Div(
                Span("COLLECTIVE UNIFORMS", cls="text-xs font-heading font-bold tracking-[0.4em] text-[#D4AF37] uppercase block mb-3"),
                H1("UBH APPAREL", cls="font-heading text-4xl sm:text-6xl md:text-7xl font-black tracking-tight text-white uppercase mb-6"),
                Div(
                    H2("DROP 01 — COMING SOON", cls="font-heading font-black text-xl md:text-2xl text-white tracking-widest uppercase mb-4"),
                    P(
                        "The official Unicorn Bounty Hunters collective uniform. Heavyweight Gray and Beige colorways are currently in production. Join the Hunt to be notified when the limited run goes live.",
                        cls="text-neutral-300 text-sm md:text-base leading-relaxed mb-8 max-w-md mx-auto"
                    ),
                    Button(
                        "GET DROP ALERT",
                        onclick="document.getElementById('email-capture-modal').style.display='block'",
                        cls="btn-gold text-xs tracking-widest py-3 px-8 cursor-pointer"
                    ),
                    cls="border border-[#1F1F1F] bg-[#0D0D0D] p-8 md:p-14 rounded-2xl shadow-2xl max-w-2xl mx-auto gold-glow"
                ),
                cls="text-center"
            ),
            cls="max-w-5xl mx-auto px-6 py-16 md:py-28"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("UBH Merch & Apparel", content, current_path="/merch")

# ----------------- Dynamic Artist Profile Routes -----------------
@rt("/roster/{artist_slug}")
def get_artist_profile(artist_slug: str):
    """Dynamic artist profile page with posts feed and social sharing."""
    artist = get_artist_by_slug(artist_slug)
    if not artist:
        # 404 fallback - show roster page with error
        error_content = Div(
            Div(
                Span("404", cls="text-6xl font-heading font-black text-[#D4AF37] block mb-4"),
                H1("ARTIST NOT FOUND", cls="font-heading text-2xl font-black text-white uppercase mb-3"),
                P(f'No artist found for "{artist_slug}". Check the roster below.', cls="text-neutral-400 text-sm mb-6"),
                A("← BACK TO ROSTER", href="/roster", cls="btn-gold text-xs py-2.5 px-6 font-heading font-bold tracking-widest"),
                cls="text-center py-20"
            ),
            RosterSection(),
            cls="w-full min-h-screen bg-[#0A0A0A]"
        )
        return Layout("Artist Not Found | UBH", error_content, current_path="/roster")

    posts = get_artist_posts(artist_slug)
    profile_view = ArtistProfilePage(artist, posts)

    return Layout(
        f"{artist['name']} | UBH Roster",
        profile_view,
        current_path="/roster"
    )

# ----------------- Roster Listing Page -----------------
@rt("/roster")
def get_roster_page():
    """Full roster listing page."""
    content = Div(
        RosterSection(),
        cls="w-full min-h-screen bg-[#0A0A0A] pt-8"
    )
    return Layout("The UBH Roster", content, current_path="/roster")

# ----------------- Subscribe API -----------------
@rt("/subscribe")
async def post_subscribe(req):
    form = await req.form()
    email = form.get("email", "")
    if not email:
        return JSONResponse({"success": False, "error": "Email is required"}, status_code=400)

    success = add_subscriber(email)
    if success:
        return JSONResponse({"success": True, "message": "Subscribed successfully!"})
    else:
        return JSONResponse({"success": False, "error": "Invalid email address."}, status_code=400)
