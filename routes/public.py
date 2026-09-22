from fasthtml.common import *
from starlette.responses import JSONResponse
import datetime

from components.base import Layout
from components.roster import RosterSection, NewsCarousel, get_artist_by_slug, ROSTER_ARTISTS
from components.calendar import BookingCalendar
from components.player import YouTubeShowcasePlayer, BandcampVaultPlayer
from components.artist_profile import ArtistProfilePage
from services.firebase_service import (
    get_slots_for_date,
    get_events,
    get_showcases,
    add_subscriber,
    get_artist_posts,
    get_recent_artist_posts,
    get_dispatches,
    get_dispatch_by_id,
    increment_dispatch_views
)
import re as _re

# YouTube ID extractor for thumbnail generation
_YT_VIDEO_RE = _re.compile(
    r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/\n\s]+/\S+/|(?:v|e(?:mbed)?|shorts)/|\S*?[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})',
    _re.IGNORECASE
)

def _extract_yt_id(url: str) -> str:
    """Extract 11-char YouTube video ID from a URL. Returns empty string if not found."""
    if not url:
        return ""
    m = _YT_VIDEO_RE.search(url)
    return m.group(1) if m else ""

def _dispatch_thumbnail(d: dict) -> str:
    """Resolve thumbnail URL: custom → YouTube auto → fallback gradient placeholder."""
    if d.get("thumbnail_url"):
        return d["thumbnail_url"]
    yt_id = _extract_yt_id(d.get("video_url", ""))
    if yt_id:
        return f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
    return ""

def _dispatch_embed_url(d: dict) -> str:
    """Generate embeddable video URL from a dispatch's video_url."""
    url = d.get("video_url", "")
    yt_id = _extract_yt_id(url)
    if yt_id:
        return f"https://www.youtube.com/embed/{yt_id}?rel=0&modestbranding=1"
    # Direct MP4 or other URL — return as-is for <video> tag
    return url

CATEGORY_COLORS = {
    "Cypher": ("bg-fuchsia-500/20 text-fuchsia-400 border-fuchsia-500/40", "🎤"),
    "Exclusive": ("bg-amber-500/20 text-amber-400 border-amber-500/40", "⚡"),
    "Behind The Scenes": ("bg-cyan-500/20 text-cyan-400 border-cyan-500/40", "🎬"),
    "Drop": ("bg-emerald-500/20 text-emerald-400 border-emerald-500/40", "💿"),
}

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

    # 5 Most Recent Artist Posts Carousel
    recent_posts = get_recent_artist_posts(limit=5)
    news_carousel = NewsCarousel(recent_posts)

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

    return Layout("Official Collective & Studio", hero_section, news_carousel, roster, showcase_teaser, current_path="/")

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

# ----------------- Rap Funxtion Dispatch Feed -----------------

def _dispatch_card(d: dict, compact: bool = False) -> Div:
    """Render a single dispatch feed card."""
    thumb = _dispatch_thumbnail(d)
    cat = d.get("category_tag", "Drop")
    cat_cls, cat_icon = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Drop"])
    date_str = d.get("created_at", "")[:10]
    views = d.get("views", 0)

    if compact:
        # Compact card for recommendation rail
        return A(
            Div(
                Div(
                    Img(src=thumb, alt=d.get("title", ""), cls="w-full h-full object-cover") if thumb else Div(cls="w-full h-full bg-gradient-to-br from-[#1A1A1A] to-[#0D0D0D]"),
                    cls="w-24 h-14 rounded-lg overflow-hidden flex-shrink-0 border border-[#222222]"
                ),
                Div(
                    H4(d.get("title", "Untitled"), cls="font-heading font-bold text-xs text-white leading-tight line-clamp-2 mb-1"),
                    Span(d.get("author", ""), cls="text-[10px] text-neutral-500 font-body"),
                    cls="flex-grow min-w-0"
                ),
                cls="flex gap-3 items-start p-2 bg-[#0D0D0D] hover:bg-[#141414] border border-[#1A1A1A] hover:border-[#D4AF37]/30 rounded-lg transition-all"
            ),
            href=f"/rap-funxtion/watch/{d.get('id', '')}",
            cls="block"
        )

    # Full-width feed card
    return A(
        Div(
            # Thumbnail
            Div(
                Img(src=thumb, alt=d.get("title", ""), cls="w-full h-full object-cover") if thumb else Div(cls="w-full h-full bg-gradient-to-br from-[#1A1A1A] to-[#0D0D0D]"),
                # Play overlay
                Div(
                    Span("▶", cls="text-white text-xl"),
                    cls="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                ),
                cls="relative w-full sm:w-64 md:w-72 aspect-video rounded-xl overflow-hidden flex-shrink-0 border border-[#222222] group-hover:border-[#D4AF37]/40 transition-colors"
            ),
            # Meta
            Div(
                # Category tag
                Span(
                    f"{cat_icon} {cat.upper()}",
                    cls=f"text-[10px] font-mono font-bold tracking-wider px-2.5 py-1 rounded-full border inline-block mb-3 {cat_cls}"
                ),
                H3(d.get("title", "Untitled"), cls="font-heading font-bold text-lg md:text-xl text-white uppercase leading-tight mb-2 group-hover:text-[#D4AF37] transition-colors"),
                Div(
                    Span(d.get("author", ""), cls="text-xs font-body text-neutral-300 font-semibold"),
                    Span("•", cls="text-neutral-600 text-xs mx-2"),
                    Span(f"👁 {views:,}", cls="text-xs font-mono text-neutral-500"),
                    Span("•", cls="text-neutral-600 text-xs mx-2"),
                    Span(date_str, cls="text-xs font-mono text-neutral-500"),
                    cls="flex items-center flex-wrap gap-y-1"
                ),
                cls="flex-grow flex flex-col justify-center py-2"
            ),
            cls="flex flex-col sm:flex-row gap-4 md:gap-6 p-4 md:p-5 bg-[#0D0D0D] hover:bg-[#111111] border border-[#1A1A1A] hover:border-[#D4AF37]/30 rounded-2xl transition-all"
        ),
        href=f"/rap-funxtion/watch/{d.get('id', '')}",
        cls="block group"
    )

@rt("/rap-funxtion")
def get_rap_funxtion():
    dispatches = get_dispatches(limit=20)

    # Build feed cards or empty state
    if dispatches:
        feed_items = Div(
            *[_dispatch_card(d) for d in dispatches],
            cls="space-y-4"
        )
    else:
        feed_items = Div(
            Div(
                Span("📡", cls="text-4xl block mb-4"),
                H3("NO ACTIVE BROADCASTS", cls="font-heading font-black text-xl text-white uppercase mb-2"),
                P("Check back soon for new cyphers, exclusives, and underground dispatches.", cls="text-neutral-400 text-sm"),
                cls="text-center p-12 bg-[#0D0D0D] border border-[#1A1A1A] rounded-2xl"
            ),
            id="empty-feed"
        )

    content = Div(
        Div(
            # Header
            Div(
                Span("RAP FUNXTION MEDIA NETWORK", cls="text-xs font-heading font-bold tracking-[0.4em] text-[#D4AF37] uppercase block mb-3"),
                H1("RAP FUNXTION DISPATCHES", cls="font-heading text-4xl sm:text-5xl md:text-7xl font-black tracking-tight text-white uppercase mb-4"),
                P(
                    "Raw cyphers, studio sessions, and exclusive underground dispatches.",
                    cls="text-neutral-400 text-sm md:text-base max-w-2xl mx-auto leading-relaxed"
                ),
                Span(f"{len(dispatches)} DISPATCH{'ES' if len(dispatches) != 1 else ''} LIVE", cls="font-mono text-[10px] text-[#D4AF37] bg-[#1A1A1A] border border-[#D4AF37]/40 px-3 py-1.5 rounded-full inline-block mt-4 font-bold tracking-wider") if dispatches else None,
                cls="text-center mb-12"
            ),
            # Feed
            feed_items,
            cls="max-w-4xl mx-auto px-6 py-12 md:py-20"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout("Rap Funxtion Dispatches", content, current_path="/rap-funxtion")

# ----------------- Dispatch Watch / Player Page -----------------
@rt("/rap-funxtion/watch/{dispatch_id}")
def get_dispatch_watch(dispatch_id: str):
    dispatch = get_dispatch_by_id(dispatch_id)
    if not dispatch:
        error_content = Div(
            Div(
                Span("404", cls="text-6xl font-heading font-black text-[#D4AF37] block mb-4"),
                H1("DISPATCH NOT FOUND", cls="font-heading text-2xl font-black text-white uppercase mb-3"),
                P("This dispatch may have been removed or the link is invalid.", cls="text-neutral-400 text-sm mb-6"),
                A("← BACK TO DISPATCHES", href="/rap-funxtion", cls="btn-gold text-xs py-2.5 px-6 font-heading font-bold tracking-widest"),
                cls="text-center py-20"
            ),
            cls="w-full min-h-screen bg-[#0A0A0A]"
        )
        return Layout("Dispatch Not Found", error_content, current_path="/rap-funxtion")

    # Increment view counter
    increment_dispatch_views(dispatch_id)

    embed_url = _dispatch_embed_url(dispatch)
    is_yt = bool(_extract_yt_id(dispatch.get("video_url", "")))
    cat = dispatch.get("category_tag", "Drop")
    cat_cls, cat_icon = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Drop"])
    views = dispatch.get("views", 0) + 1  # Show post-increment count
    date_str = dispatch.get("created_at", "")[:10]

    # Video player
    if is_yt:
        player = Iframe(
            src=embed_url,
            allowfullscreen="true",
            cls="w-full aspect-video rounded-2xl border border-[#222222] shadow-2xl"
        )
    else:
        player = Video(
            Source(src=embed_url, type="video/mp4"),
            controls=True,
            cls="w-full aspect-video rounded-2xl border border-[#222222] shadow-2xl bg-black"
        )

    # Next dispatches rail
    all_dispatches = get_dispatches(limit=10)
    next_dispatches = [d for d in all_dispatches if d.get("id") != dispatch_id][:5]

    rail = Div(
        H3("NEXT DISPATCHES", cls="font-heading font-bold text-sm text-[#D4AF37] uppercase tracking-wider mb-4"),
        Div(
            *[_dispatch_card(d, compact=True) for d in next_dispatches],
            cls="space-y-2"
        ) if next_dispatches else P("No other dispatches available.", cls="text-neutral-500 text-xs italic"),
        A("← ALL DISPATCHES", href="/rap-funxtion", cls="text-[10px] font-heading font-bold text-[#D4AF37] hover:text-[#FFD700] tracking-widest mt-4 block"),
        cls="w-full lg:w-80 flex-shrink-0"
    )

    content = Div(
        Div(
            # Back link
            Div(
                A("← DISPATCHES", href="/rap-funxtion", cls="text-xs font-heading font-bold text-neutral-400 hover:text-[#D4AF37] tracking-widest transition-colors"),
                cls="mb-6"
            ),
            # Main layout: player + rail
            Div(
                # Player column
                Div(
                    player,
                    # Dispatch meta below player
                    Div(
                        Span(
                            f"{cat_icon} {cat.upper()}",
                            cls=f"text-[10px] font-mono font-bold tracking-wider px-2.5 py-1 rounded-full border inline-block mb-3 {cat_cls}"
                        ),
                        H1(dispatch.get("title", ""), cls="font-heading font-bold text-xl md:text-2xl text-white uppercase leading-tight mb-3"),
                        Div(
                            Span(dispatch.get("author", ""), cls="text-sm font-body text-neutral-200 font-semibold"),
                            Span("•", cls="text-neutral-600 mx-2"),
                            Span(f"👁 {views:,}", cls="text-sm font-mono text-neutral-400"),
                            Span("•", cls="text-neutral-600 mx-2"),
                            Span(date_str, cls="text-sm font-mono text-neutral-400"),
                            cls="flex items-center flex-wrap gap-y-1"
                        ),
                        cls="mt-6"
                    ),
                    cls="flex-grow min-w-0"
                ),
                # Recommendation rail
                rail,
                cls="flex flex-col lg:flex-row gap-8"
            ),
            cls="max-w-6xl mx-auto px-6 py-10 md:py-16"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )

    return Layout(f"{dispatch.get('title', 'Dispatch')} | Rap Funxtion", content, current_path="/rap-funxtion")

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
