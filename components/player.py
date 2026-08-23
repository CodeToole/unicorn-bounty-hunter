from fasthtml.common import *
from typing import List, Dict, Any

def YouTubeShowcasePlayer(youtube_id: str, title: str = "Musical Chairs Cypher Series", description: str = ""):
    if "videoseries" in youtube_id or "list=" in youtube_id:
        embed_src = f"https://www.youtube.com/embed/{youtube_id}" if "videoseries" in youtube_id else f"https://www.youtube.com/embed/videoseries?list={youtube_id}"
    else:
        embed_src = f"https://www.youtube.com/embed/{youtube_id}?rel=0&modestbranding=1"

    return Div(
        Div(
            Iframe(
                src=embed_src,
                title=title or "UBH Showcase Player",
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
                allowfullscreen="true",
                cls="w-full aspect-video rounded-xl shadow-2xl border border-[#222222]"
            ),
            cls="w-full bg-[#0D0D0D] p-2 md:p-3 rounded-2xl border border-[#1F1F1F] shadow-2xl"
        ),
        Div(
            H3(title, cls="font-heading font-bold text-lg md:text-xl text-white mt-4") if title else None,
            P(description, cls="text-neutral-400 text-xs md:text-sm mt-1 leading-relaxed") if description else None,
            cls="px-2"
        ) if title or description else None,
        cls="w-full max-w-4xl mx-auto"
    )

def BandcampVaultPlayer():
    albums = [
        {
            "title": "Wilderness",
            "album_id": "2846109268",
            "bandcamp_url": "https://bandcamp.com/EmbeddedPlayer/album=2846109268/size=large/bgcol=333333/linkcol=FFD700/tracklist=false/transparent=true/",
            "description": "Original audio project from the UBH collective vault."
        },
        {
            "title": "Locals Only",
            "album_id": "3414750159",
            "bandcamp_url": "https://bandcamp.com/EmbeddedPlayer/album=3414750159/size=large/bgcol=333333/linkcol=FFD700/tracklist=false/transparent=true/",
            "description": "Raw underground showcase of homegrown talent and hard-hitting production."
        }
    ]

    return Div(
        Div(
            *[
                Div(
                    Div(
                        H3(album["title"], cls="font-heading font-black text-lg md:text-xl text-[#D4AF37] mb-2 text-center uppercase tracking-wide"),
                        P(album["description"], cls="text-neutral-400 text-xs text-center mb-4"),
                        Iframe(
                            src=album["bandcamp_url"],
                            style="border: 0; width: 100%; height: 470px;",
                            seamless="seamless",
                            cls="rounded-lg shadow-inner bg-[#1A1A1A]"
                        ),
                        cls="bg-[#0D0D0D] p-6 rounded-2xl border border-[#1F1F1F] hover:border-[#D4AF37]/50 transition-all duration-300 shadow-2xl flex flex-col justify-between"
                    ),
                    cls="w-full max-w-md"
                )
                for album in albums
            ],
            cls="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto justify-items-center"
        ),
        cls="w-full py-6"
    )
