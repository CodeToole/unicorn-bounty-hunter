from fasthtml.common import *
from urllib.parse import quote
from typing import Optional

def ArtistProfilePage(artist: dict, posts: list):
    """Full artist profile page with bio, posts feed, social share, and featured content."""
    name = artist["name"]
    slug = artist["slug"]
    role = artist["role"]
    handle = artist["handle"]
    image_url = artist["image_url"]
    instagram = artist["instagram"]
    full_bio = artist.get("full_bio", artist.get("bio", ""))
    featured_yt = artist.get("featured_youtube")

    return Div(
        # Hero Banner
        _artist_hero(artist),
        # Main Content Grid
        Div(
            Div(
                # Left Column: Bio + Featured
                Div(
                    _artist_bio_card(artist),
                    _featured_video_card(featured_yt, name) if featured_yt else None,
                    cls="space-y-6"
                ),
                # Right Column: Posts Feed
                Div(
                    _posts_feed(posts, slug, name),
                    cls="lg:col-span-2"
                ),
                cls="grid grid-cols-1 lg:grid-cols-3 gap-8"
            ),
            cls="max-w-7xl mx-auto px-6 py-12"
        ),
        cls="w-full min-h-screen bg-[#0A0A0A]"
    )


def _artist_hero(artist: dict):
    """Full-width hero banner with artist image and identity."""
    return Section(
        Div(
            # Gradient overlay
            Div(cls="absolute inset-0 bg-gradient-to-t from-[#0A0A0A] via-[#0A0A0A]/80 to-transparent z-10"),
            # Content
            Div(
                # Artist portrait
                Div(
                    Img(
                        src=artist["image_url"],
                        alt=f"{artist['name']} portrait",
                        cls="w-36 h-36 md:w-44 md:h-44 rounded-full object-cover border-3 border-[#D4AF37] shadow-2xl shadow-[#D4AF37]/20"
                    ),
                    cls="mb-6"
                ),
                # Name and role
                Div(
                    Div(
                        Div(cls="w-12 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60"),
                        Span(artist["role"].upper(), cls="font-body text-[#D4AF37] text-[10px] tracking-[0.4em] uppercase font-semibold"),
                        Div(cls="w-12 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60"),
                        cls="flex items-center justify-center gap-3 mb-3"
                    ),
                    H1(artist["name"].upper(), cls="font-heading text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-white uppercase"),
                    cls="text-center"
                ),
                # Action buttons
                Div(
                    A(
                        Span("📸"),
                        Span(f" {artist['handle']}"),
                        href=artist["instagram"],
                        target="_blank",
                        rel="noopener noreferrer",
                        cls="bg-gradient-to-r from-[#833AB4] via-[#FD1D1D] to-[#F77737] text-white text-xs font-heading font-bold tracking-wider px-5 py-2.5 rounded-lg hover:opacity-90 transition-opacity inline-flex items-center gap-1"
                    ),
                    A(
                        "← BACK TO ROSTER",
                        href="/roster",
                        cls="btn-gold-outline text-[10px] py-2 px-4 font-heading font-bold tracking-widest"
                    ),
                    cls="flex flex-wrap items-center justify-center gap-3 mt-6"
                ),
                cls="relative z-20 flex flex-col items-center text-center"
            ),
            cls="relative py-20 md:py-28 flex items-center justify-center overflow-hidden"
        ),
        cls="w-full relative"
    )


def _artist_bio_card(artist: dict):
    """Sidebar bio card."""
    full_bio = artist.get("full_bio", artist.get("bio", ""))
    paragraphs = full_bio.split("\n") if full_bio else []

    return Div(
        Div(
            Span("ABOUT", cls="text-[#D4AF37] text-[10px] font-heading font-bold tracking-[0.3em] uppercase block mb-3"),
            Div(cls="w-8 h-[1px] bg-[#222] mb-4"),
            *[P(p, cls="text-neutral-300 text-sm leading-relaxed mb-3") for p in paragraphs if p.strip()],
            cls="p-6"
        ),
        cls="bg-[#0D0D0D] border border-[#1A1A1A] rounded-xl overflow-hidden"
    )


def _featured_video_card(youtube_id: str, artist_name: str):
    """Sidebar featured video embed."""
    is_playlist = youtube_id.startswith("videoseries")
    embed_url = f"https://www.youtube.com/embed/{youtube_id}"

    return Div(
        Div(
            Span("FEATURED", cls="text-[#D4AF37] text-[10px] font-heading font-bold tracking-[0.3em] uppercase block mb-3"),
            Div(cls="w-8 h-[1px] bg-[#222] mb-4"),
            Div(
                Iframe(
                    src=embed_url,
                    title=f"{artist_name} featured content",
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture",
                    allowfullscreen=True,
                    cls="absolute inset-0 w-full h-full rounded-lg"
                ),
                cls="relative w-full pb-[56.25%] bg-black rounded-lg overflow-hidden"
            ),
            cls="p-6"
        ),
        cls="bg-[#0D0D0D] border border-[#1A1A1A] rounded-xl overflow-hidden"
    )


def _posts_feed(posts: list, artist_slug: str, artist_name: str):
    """Main content area: artist post feed with social sharing."""
    if not posts:
        empty_state = Div(
            Div(
                Span("📝", cls="text-4xl block mb-3"),
                H3("NO POSTS YET", cls="font-heading text-lg font-bold text-white uppercase mb-2"),
                P(f"{artist_name} hasn't published any posts yet. Check back soon.", cls="text-neutral-400 text-sm"),
                cls="text-center py-16"
            ),
            cls="bg-[#0D0D0D] border border-[#1A1A1A] rounded-xl"
        )
        return Div(
            Span("LATEST POSTS", cls="text-[#D4AF37] text-[10px] font-heading font-bold tracking-[0.3em] uppercase block mb-4"),
            empty_state,
            # SSE feed target
            Div(id=f"artist-feed-{artist_slug}"),
        )

    return Div(
        Div(
            Span("LATEST POSTS", cls="text-[#D4AF37] text-[10px] font-heading font-bold tracking-[0.3em] uppercase block mb-1"),
            Span(f"{len(posts)} published", cls="text-neutral-500 text-[10px] font-body tracking-wider uppercase"),
            cls="flex items-baseline gap-3 mb-5"
        ),
        # Posts list
        Div(
            *[_post_card(post, idx) for idx, post in enumerate(posts)],
            id=f"artist-feed-{artist_slug}",
            cls="space-y-5"
        ),
    )


def _post_card(post: dict, idx: int = 0):
    """Individual post card with social share toolbar."""
    post_id = post.get("id", f"post-{idx}")
    title = post.get("title", "Untitled")
    body = post.get("body", "")
    media_url = post.get("media_url", "")
    created_at = post.get("created_at", "")
    artist_slug = post.get("artist_slug", "")

    # Format date
    date_display = created_at[:10] if created_at else ""

    # Paragraphs
    paragraphs = [p for p in body.split("\n") if p.strip()]

    # Build the canonical post URL for sharing
    post_url = f"/roster/{artist_slug}#post-{post_id}"

    return Div(
        Div(
            # Post header
            Div(
                H3(title, cls="font-heading text-lg md:text-xl font-bold text-white uppercase tracking-tight"),
                Span(date_display, cls="text-neutral-500 text-[10px] font-mono tracking-wider shrink-0 mt-1"),
                cls="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-4"
            ),
            # Media image (if present)
            Div(
                Img(
                    src=media_url,
                    alt=f"{title} media",
                    cls="w-full h-48 md:h-56 object-cover rounded-lg"
                ),
                cls="mb-4 overflow-hidden rounded-lg"
            ) if media_url else None,
            # Body text
            Div(
                *[P(p, cls="text-neutral-300 text-sm leading-relaxed mb-2") for p in paragraphs],
                cls="mb-5"
            ),
            # Divider
            Div(cls="w-full h-[1px] bg-[#1A1A1A] mb-4"),
            # Social Share Toolbar
            _share_toolbar(title, post_url, post_id),
            cls="p-6 md:p-7"
        ),
        id=f"post-{post_id}",
        cls="bg-[#0D0D0D] border border-[#1A1A1A] rounded-xl hover:border-[#222] transition-colors duration-200"
    )


def _share_toolbar(title: str, post_url: str, post_id: str):
    """Social Share Toolbar: Web Share API, X, Facebook, Copy Link."""
    encoded_title = quote(title)
    # Use a placeholder base URL; in production this resolves to the real domain
    full_url_js = f"window.location.origin + '{post_url}'"
    encoded_post_url = quote(post_url)

    share_btn_cls = "text-[10px] font-heading font-bold tracking-wider px-3 py-1.5 rounded-md transition-all duration-200 inline-flex items-center gap-1.5 cursor-pointer"

    return Div(
        Span("SHARE", cls="text-neutral-600 text-[9px] font-heading font-bold tracking-[0.3em] uppercase"),
        Div(
            # Native Web Share (mobile-first)
            Button(
                Span("📤"),
                Span(" Share"),
                cls=f"{share_btn_cls} bg-[#141414] text-neutral-300 hover:bg-[#1A1A1A] hover:text-white web-share-btn",
                onclick=f"""
                    if (navigator.share) {{
                        navigator.share({{
                            title: '{title.replace("'", "\\'")}',
                            url: {full_url_js}
                        }}).catch(function(){{}});
                    }} else {{
                        alert('Web Share is not supported in this browser. Use the links below.');
                    }}
                """,
                type="button"
            ),
            # X (Twitter)
            A(
                Span("𝕏"),
                Span(" Post"),
                href=f"https://x.com/intent/tweet?text={encoded_title}&url={encoded_post_url}",
                target="_blank",
                rel="noopener noreferrer",
                cls=f"{share_btn_cls} bg-[#141414] text-neutral-300 hover:bg-[#1A1A1A] hover:text-white"
            ),
            # Facebook
            A(
                Span("f"),
                Span(" Share"),
                href=f"https://www.facebook.com/sharer/sharer.php?u={encoded_post_url}",
                target="_blank",
                rel="noopener noreferrer",
                cls=f"{share_btn_cls} bg-[#141414] text-neutral-300 hover:bg-[#1A1A1A] hover:text-white"
            ),
            # Copy Link
            Button(
                Span("🔗"),
                Span(" Copy Link", id=f"copy-label-{post_id}"),
                cls=f"{share_btn_cls} bg-[#141414] text-neutral-300 hover:bg-[#1A1A1A] hover:text-[#D4AF37]",
                onclick=f"""
                    var url = window.location.origin + '{post_url}';
                    navigator.clipboard.writeText(url).then(function() {{
                        var label = document.getElementById('copy-label-{post_id}');
                        label.textContent = ' Copied!';
                        label.style.color = '#D4AF37';
                        setTimeout(function() {{
                            label.textContent = ' Copy Link';
                            label.style.color = '';
                        }}, 2000);
                    }});
                """,
                type="button"
            ),
            cls="flex flex-wrap items-center gap-2"
        ),
        cls="flex flex-col sm:flex-row sm:items-center gap-3"
    )
