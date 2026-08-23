from fasthtml.common import *

def Navbar(current_path: str = "/"):
    nav_links = [
        ("/services", "SERVICES & STUDIO"),
        ("/showcase", "SHOWCASE"),
        ("/rap-funxtion", "RAP FUNXTION"),
        ("/music", "THE VAULT"),
        ("/merch", "MERCH"),
    ]

    def _render_link(href: str, label: str):
        is_active = current_path == href or (href == "/showcase" and current_path == "/musical-chairs")
        active_cls = "text-[#D4AF37] font-bold border-b-2 border-[#D4AF37] pb-1" if is_active else "text-neutral-400 hover:text-white transition-colors duration-200"
        return A(
            label,
            href=href,
            cls=f"text-xs tracking-[0.25em] font-heading uppercase {active_cls}"
        )

    def _render_mobile_link(href: str, label: str):
        short_label = label.replace("SERVICES & STUDIO", "STUDIO").replace("THE VAULT", "MUSIC").replace("RAP FUNXTION", "RAP FX")
        is_active = current_path == href or (href == "/showcase" and current_path == "/musical-chairs")
        active_cls = "text-[#D4AF37] font-bold" if is_active else "text-neutral-400 hover:text-white"
        return A(
            short_label,
            href=href,
            cls=f"text-[10px] tracking-wider font-heading uppercase py-1 px-1.5 whitespace-nowrap {active_cls}"
        )

    return Header(
        Div(
            # Brand Header / Logo
            Div(
                A(
                    Span("UBH", cls="text-2xl md:text-3xl font-black font-heading tracking-tighter text-white hover:text-[#D4AF37] transition-colors"),
                    Span(" • COLLECTIVE", cls="hidden lg:inline text-[10px] tracking-[0.3em] text-[#D4AF37] font-heading ml-2"),
                    href="/",
                    cls="flex items-center group cursor-pointer"
                ),
                cls="flex items-center"
            ),
            # Desktop Navigation Links
            Nav(
                *[_render_link(h, l) for h, l in nav_links],
                A("BOOK NOW", href="/booking", cls="btn-gold py-1.5 px-4 text-xs ml-4 font-heading"),
                cls="hidden md:flex items-center gap-6"
            ),
            # Mobile Navigation Row
            Nav(
                *[_render_mobile_link(h, l) for h, l in nav_links],
                A("BOOK", href="/booking", cls="text-[10px] bg-[#D4AF37] text-black font-bold px-2 py-1 rounded uppercase tracking-wider"),
                cls="flex md:hidden items-center gap-2 overflow-x-auto"
            ),
            cls="max-w-7xl mx-auto px-4 sm:px-6 h-16 md:h-20 flex items-center justify-between"
        ),
        cls="fixed top-0 left-0 right-0 z-50 bg-[#0A0A0A]/95 backdrop-blur-md border-b border-[#1A1A1A] w-full"
    )
