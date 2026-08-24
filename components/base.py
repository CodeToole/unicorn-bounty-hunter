from fasthtml.common import *
from components.navbar import Navbar
from components.footer import SiteFooter
from components.email_capture import EmailCaptureModal, EmailCaptureWidget

def Layout(title: str, *content, current_path: str = "/", show_nav: bool = True, show_footer: bool = True, show_capture: bool = True):
    page_title = f"Unicorn Bounty Hunters | {title}" if title else "Unicorn Bounty Hunters (UBH) — Music, Studio & Live Events"
    
    tailwind_script = Script("""
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        gold: '#D4AF37',
                        'gold-bright': '#FFD700',
                        'obsidian': '#0A0A0A',
                        'obsidian-dark': '#050505',
                        'obsidian-card': '#0D0D0D',
                        'obsidian-hover': '#141414',
                    },
                    fontFamily: {
                        heading: ['"Space Grotesk"', 'sans-serif'],
                        body: ['Manrope', 'sans-serif'],
                    }
                }
            }
        }
    """)

    return Title(page_title), Head(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1, maximum-scale=1"),
        Meta(name="description", content="Unicorn Bounty Hunters (UBH) — Independent music collective, recording studio, Rap Funxtion live showcases & creative powerhouse."),
        Meta(name="theme-color", content="#0A0A0A"),
        # Google Fonts
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;900&display=swap"),
        # Tailwind CSS CDN
        Script(src="https://cdn.tailwindcss.com"),
        tailwind_script,
        # Datastar Hypermedia Engine CDN (v1.x beta)
        Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-beta.1/bundles/datastar.js"),
        # UBH Custom Design System
        Link(rel="stylesheet", href="/static/css/theme.css"),
        Link(rel="icon", type="image/x-icon", href="/static/assets/favicon.ico"),
        Link(rel="icon", type="image/png", href="/static/assets/favicon.png"),
        Link(rel="apple-touch-icon", href="/static/assets/apple-touch-icon.png"),
    ), Body(
        Navbar(current_path=current_path) if show_nav else None,
        Main(
            *content,
            cls="w-full flex-grow flex flex-col pt-16 md:pt-20" if show_nav else "w-full flex-grow flex flex-col"
        ),
        SiteFooter() if show_footer else None,
        EmailCaptureWidget() if show_capture else None,
        EmailCaptureModal() if show_capture else None,
        cls="bg-[#0A0A0A] text-white font-body min-h-screen flex flex-col antialiased selection:bg-[#D4AF37] selection:text-black overflow-x-hidden"
    )
