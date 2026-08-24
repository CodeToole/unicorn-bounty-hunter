from fasthtml.common import *
from typing import Optional

ROSTER_ARTISTS = [
    {
        "name": "Ali Kazem",
        "slug": "ali-kazem",
        "handle": "@shadowurameshi",
        "role": "Founder / Executive Producer",
        "image_url": "/static/assets/ali.jpg",
        "instagram": "https://instagram.com/shadowurameshi",
        "bio": "Visionary executive producer and architect behind the Unicorn Bounty Hunters movement and Rap Funxtion showcase series.",
        "full_bio": "Ali Kazem is the founding executive producer and strategic mastermind behind the Unicorn Bounty Hunters collective. From curating the Rap Funxtion live showcase series to engineering the sonic identity of UBH, Ali operates at the intersection of underground culture and high-production artistry. His vision for independent hip-hop fuses meticulous sound design with raw, uncompromising creative direction. As the primary architect of the collective's operations, Ali oversees studio sessions, artist development pipelines, and the strategic expansion of the UBH brand across digital and live performance platforms.",
        "featured_youtube": "videoseries?list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1",
    },
    {
        "name": "Malik Rose",
        "slug": "malik-rose",
        "handle": "@gentlemanrosayy",
        "role": "Vocalist / A&R",
        "image_url": "/static/assets/malik.jpg",
        "instagram": "https://instagram.com/gentlemanrosayy",
        "bio": "Soulful vocalist, melodic lyricist, and talent curator directing artist development across the collective.",
        "full_bio": "Malik Rose brings soulful resonance and melodic precision to every UBH project. As the collective's primary vocalist and A&R director, he is responsible for identifying emerging underground talent, shaping the creative direction of collaborative records, and delivering performances that bridge raw emotion with refined musicality. His ear for melody and instinct for artist development have made him the connective tissue between the UBH production floor and the broader independent hip-hop landscape.",
        "featured_youtube": None,
    },
    {
        "name": "Unkn0wn Da Rapper",
        "slug": "unkn0wn",
        "handle": "@unkn0wndaproducer",
        "role": "Producer / Engineer",
        "image_url": "/static/assets/unknown.jpg",
        "instagram": "https://instagram.com/unkn0wndaproducer",
        "bio": "Master audio engineer, sonic architect, and sound designer powering the core UBH production line.",
        "full_bio": "Unkn0wn Da Rapper is the sonic architect behind the UBH production line. As lead producer and audio engineer, he commands the studio with surgical precision — crafting beats, mixing vocals, and mastering final outputs that define the collective's signature sound. His production style blends hard-hitting 808 patterns with atmospheric layering, creating immersive sonic landscapes that push underground hip-hop forward. Every UBH release passes through his hands before it reaches the world.",
        "featured_youtube": None,
    },
    {
        "name": "Yung Illie",
        "slug": "yung-illie",
        "handle": "@illieaking",
        "role": "Lyricist / Creative Director",
        "image_url": "/static/assets/illie.png",
        "instagram": "https://instagram.com/illieaking",
        "bio": "Dynamic lyricist and visual creative director defining the raw aesthetic of underground hip-hop.",
        "full_bio": "Yung Illie is the lyrical engine and creative director of the Unicorn Bounty Hunters. His writing fuses dense wordplay, narrative storytelling, and unapologetic street poetry into verses that hit with both intellect and intensity. Beyond the mic, Illie shapes the visual identity of UBH — directing content aesthetics, brand imagery, and the overall creative narrative that distinguishes the collective from the mainstream. He embodies the raw, unfiltered spirit at the core of UBH culture.",
        "featured_youtube": None,
    }
]

# Lookup map for O(1) slug access
_ARTIST_BY_SLUG = {a["slug"]: a for a in ROSTER_ARTISTS}

def get_artist_by_slug(slug: str) -> Optional[dict]:
    """Return artist data dict for a given slug, or None if not found."""
    return _ARTIST_BY_SLUG.get(slug)

def get_all_slugs() -> list[str]:
    """Return list of all valid artist slugs."""
    return list(_ARTIST_BY_SLUG.keys())

def RosterSection():
    return Section(
        Div(
            # Decorative Section Header
            Div(
                Div(
                    Div(cls="w-16 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60"),
                    Span("THE COUNCIL", cls="font-body text-[#D4AF37] text-xs tracking-[0.4em] uppercase font-semibold"),
                    Div(cls="w-16 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60"),
                    cls="flex items-center justify-center gap-4 mb-4"
                ),
                H2("THE UBH ROSTER", cls="font-heading text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black tracking-tight uppercase text-white"),
                P("Four visionaries forging the gold standard in independent audio and live performance.", cls="text-neutral-400 text-sm md:text-base mt-4 max-w-xl mx-auto"),
                cls="max-w-7xl mx-auto px-6 mb-14 text-center"
            ),
            # Cards Grid
            Div(
                *[_build_artist_card(artist) for artist in ROSTER_ARTISTS],
                cls="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 px-6 max-w-7xl mx-auto"
            ),
            cls="py-16 md:py-24"
        ),
        cls="w-full relative z-20"
    )

def _build_artist_card(artist: dict):
    profile_url = f"/roster/{artist['slug']}"
    return A(
        Div(
            # Artist Portrait Image
            Div(
                Img(
                    src=artist["image_url"],
                    alt=f"{artist['name']} portrait",
                    cls="w-28 h-28 md:w-32 md:h-32 rounded-full object-cover border-2 border-[#222222] group-hover:border-[#D4AF37] transition-all duration-300 shadow-xl"
                ),
                cls="relative mb-5 flex justify-center"
            ),
            # Name
            H3(artist["name"], cls="font-heading text-lg md:text-xl font-bold tracking-tight text-white uppercase mb-1"),
            # Role Tag
            Span(artist["role"], cls="font-body text-neutral-400 text-xs tracking-wider uppercase mb-3 block"),
            # Divider
            Div(cls="w-10 h-[1px] bg-[#222222] group-hover:bg-[#D4AF37]/60 transition-colors duration-300 mb-3 mx-auto"),
            # Bio snippet
            P(artist.get("bio", ""), cls="text-neutral-400 text-xs leading-relaxed mb-4 text-center line-clamp-3"),
            # View Profile CTA
            Span("VIEW PROFILE", cls="text-xs font-heading font-bold tracking-widest text-[#D4AF37] group-hover:text-[#FFD700] transition-colors mt-auto"),
            cls="bg-[#0D0D0D] border border-[#1E1E1E] hover:border-[#D4AF37]/80 transition-all duration-300 p-8 rounded-xl flex flex-col items-center text-center h-full card-hover-gold"
        ),
        href=profile_url,
        cls="group relative block no-underline"
    )

def NewsCarousel(posts: list):
    """
    Dynamic 'LATEST FROM THE HUNT' ticker/carousel banner for the homepage.
    Renders recent posts with Publishing Artist Name, Post Title, Short Snippet,
    and a 'READ ARTICLE' button routing to /roster/{artist_slug}#post-{id}.
    """
    if not posts:
        return Div(cls="hidden")

    # Build slides
    slides = []
    dots = []
    for idx, post in enumerate(posts):
        post_id = post.get("id", f"post-{idx}")
        title = post.get("title", "Untitled Transmission")
        body = post.get("body", "")
        snippet = (body[:130] + "...") if len(body) > 130 else body
        artist_slug = post.get("artist_slug", "")
        artist = get_artist_by_slug(artist_slug)
        artist_name = artist["name"] if artist else artist_slug.replace("-", " ").title()
        artist_img = artist.get("image_url", "/static/assets/ubh_logo.jpg") if artist else "/static/assets/ubh_logo.jpg"
        media_url = post.get("media_url", "")
        read_url = f"/roster/{artist_slug}#post-{post_id}"

        slide = Div(
            Div(
                # Inner Card Container
                Div(
                    # Left / Top Info: Artist & Category
                    Div(
                        Div(
                            Img(
                                src=artist_img,
                                alt=f"{artist_name} portrait",
                                cls="w-10 h-10 rounded-full object-cover border border-[#D4AF37]/50 shadow-md"
                            ),
                            Div(
                                Span(artist_name, cls="font-heading font-bold text-sm text-[#D4AF37] tracking-wider uppercase block"),
                                Span("DISPATCH TRANSMISSION", cls="font-body text-[10px] text-neutral-400 uppercase tracking-widest"),
                                cls="flex flex-col text-left"
                            ),
                            cls="flex items-center gap-3"
                        ),
                        # Timestamp / Status badge
                        Span("FIELD REPORT", cls="font-mono text-[10px] text-black bg-[#D4AF37] font-bold px-2.5 py-0.5 rounded uppercase tracking-wider hidden sm:inline-block"),
                        cls="flex items-center justify-between border-b border-[#222222] pb-3 mb-4"
                    ),
                    # Middle: Title and Snippet
                    Div(
                        H3(
                            title,
                            cls="font-heading font-black text-lg sm:text-xl md:text-2xl text-white uppercase tracking-tight mb-2 group-hover:text-[#D4AF37] transition-colors line-clamp-2"
                        ),
                        P(
                            snippet,
                            cls="text-neutral-300 text-xs sm:text-sm leading-relaxed mb-6 font-body line-clamp-3 text-left"
                        ),
                        cls="flex-grow"
                    ),
                    # Bottom Action: Read Article
                    Div(
                        A(
                            "READ ARTICLE →",
                            href=read_url,
                            cls="btn-gold text-xs py-2.5 px-6 tracking-widest inline-flex items-center gap-2 shadow-lg"
                        ),
                        cls="flex justify-start items-center pt-2"
                    ),
                    cls="p-6 md:p-8 flex flex-col justify-between h-full"
                ),
                cls="bg-[#0D0D0D]/95 border border-[#222222] hover:border-[#D4AF37]/70 rounded-2xl transition-all duration-300 shadow-2xl backdrop-blur-md h-full flex flex-col justify-between card-hover-gold"
            ),
            cls=f"carousel-slide {'block' if idx == 0 else 'hidden'} w-full transition-opacity duration-500 ease-in-out",
            id=f"hunt-slide-{idx}"
        )
        slides.append(slide)

        dot = Button(
            cls=f"carousel-dot w-3 h-3 rounded-full transition-all duration-300 cursor-pointer {'bg-[#D4AF37] w-8' if idx == 0 else 'bg-neutral-600 hover:bg-neutral-400'}",
            onclick=f"setHuntSlide({idx})",
            aria_label=f"Slide {idx + 1}"
        )
        dots.append(dot)

    carousel_script = Script(f"""
        (function() {{
            let currentSlide = 0;
            const totalSlides = {len(posts)};
            let timer = null;

            window.setHuntSlide = function(index) {{
                if (index < 0) index = totalSlides - 1;
                if (index >= totalSlides) index = 0;
                currentSlide = index;

                for (let i = 0; i < totalSlides; i++) {{
                    const slide = document.getElementById('hunt-slide-' + i);
                    if (slide) {{
                        if (i === currentSlide) {{
                            slide.classList.remove('hidden');
                            slide.classList.add('block');
                        }} else {{
                            slide.classList.remove('block');
                            slide.classList.add('hidden');
                        }}
                    }}
                }}

                const dots = document.querySelectorAll('.carousel-dot');
                dots.forEach((dot, i) => {{
                    if (i === currentSlide) {{
                        dot.className = 'carousel-dot w-8 h-3 rounded-full transition-all duration-300 cursor-pointer bg-[#D4AF37]';
                    }} else {{
                        dot.className = 'carousel-dot w-3 h-3 rounded-full transition-all duration-300 cursor-pointer bg-neutral-600 hover:bg-neutral-400';
                    }}
                }});
            }};

            window.nextHuntSlide = function() {{
                setHuntSlide(currentSlide + 1);
            }};

            window.prevHuntSlide = function() {{
                setHuntSlide(currentSlide - 1);
            }};

            function startTimer() {{
                stopTimer();
                timer = setInterval(function() {{
                    window.nextHuntSlide();
                }}, 6000);
            }}

            function stopTimer() {{
                if (timer) clearInterval(timer);
            }}

            const container = document.getElementById('hunt-carousel-wrapper');
            if (container) {{
                container.addEventListener('mouseenter', stopTimer);
                container.addEventListener('mouseleave', startTimer);
                container.addEventListener('touchstart', stopTimer, {{ passive: true }});
            }}

            startTimer();
        }})();
    """)

    return Section(
        Div(
            # Ticker / Carousel Header
            Div(
                Div(
                    Span("⚡", cls="animate-bounce text-[#D4AF37] text-sm"),
                    Span("LATEST FROM THE HUNT", cls="font-heading font-black text-xs md:text-sm text-[#D4AF37] tracking-[0.35em] uppercase"),
                    cls="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#141414] border border-[#D4AF37]/40 shadow-lg mb-3"
                ),
                H2("NEWS & FIELD DISPATCHES", cls="font-heading text-2xl sm:text-3xl md:text-4xl font-black tracking-tight uppercase text-white"),
                cls="text-center mb-8"
            ),
            # Carousel Frame & Wrapper
            Div(
                # Slides Container
                Div(
                    *slides,
                    id="hunt-slides-container",
                    cls="relative min-h-[260px] sm:min-h-[230px] flex items-center justify-center"
                ),
                # Navigation Controls (Prev / Next Arrows + Dots)
                Div(
                    Button(
                        "‹",
                        onclick="prevHuntSlide()",
                        cls="w-9 h-9 rounded-full bg-[#141414] border border-[#2A2A2A] hover:border-[#D4AF37] text-[#D4AF37] hover:text-white flex items-center justify-center font-bold text-lg transition-all duration-200 cursor-pointer shadow-md",
                        aria_label="Previous Transmission"
                    ),
                    Div(*dots, cls="flex items-center gap-2"),
                    Button(
                        "›",
                        onclick="nextHuntSlide()",
                        cls="w-9 h-9 rounded-full bg-[#141414] border border-[#2A2A2A] hover:border-[#D4AF37] text-[#D4AF37] hover:text-white flex items-center justify-center font-bold text-lg transition-all duration-200 cursor-pointer shadow-md",
                        aria_label="Next Transmission"
                    ),
                    cls="flex items-center justify-between mt-6 px-2"
                ),
                id="hunt-carousel-wrapper",
                cls="max-w-4xl mx-auto"
            ),
            carousel_script,
            cls="max-w-7xl mx-auto px-6 py-12 md:py-16"
        ),
        cls="w-full relative z-20 bg-gradient-to-b from-[#0A0A0A] via-[#0E0E0E] to-[#0A0A0A] border-t border-b border-[#1A1A1A]"
    )
