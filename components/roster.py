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
