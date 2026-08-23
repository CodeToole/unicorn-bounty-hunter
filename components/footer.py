from fasthtml.common import *

def SiteFooter():
    return Footer(
        Div(
            Div(
                # Column 1: Brand Info
                Div(
                    Div(
                        Span("UNICORN BOUNTY HUNTERS", cls="font-heading font-black text-xl tracking-wider text-white"),
                        P("Independent Creative Collective, Recording Studio & Live Showcases.", cls="text-neutral-400 text-xs mt-2 max-w-sm leading-relaxed"),
                        P("Founded by Ali Kazem. Sound Engineered for the Next Era.", cls="text-neutral-500 text-xs mt-1 font-mono"),
                        cls="flex flex-col"
                    ),
                    cls="space-y-4 md:col-span-1"
                ),
                # Column 2: Navigation Links
                Div(
                    H4("QUICK LINKS", cls="text-xs font-heading font-bold tracking-[0.2em] text-[#D4AF37] mb-4 uppercase"),
                    Ul(
                        Li(A("Studio Recording & Rates", href="/services", cls="text-xs text-neutral-400 hover:text-white transition-colors")),
                        Li(A("Musical Chairs Showcase", href="/showcase", cls="text-xs text-neutral-400 hover:text-white transition-colors")),
                        Li(A("Rap Funxtion Live", href="/rap-funxtion", cls="text-xs text-neutral-400 hover:text-white transition-colors")),
                        Li(A("The Vault (Music Catalog)", href="/music", cls="text-xs text-neutral-400 hover:text-white transition-colors")),
                        Li(A("UBH Uniform Merch", href="/merch", cls="text-xs text-neutral-400 hover:text-white transition-colors")),
                        cls="space-y-2.5 list-none p-0 m-0"
                    ),
                    cls="flex flex-col"
                ),
                # Column 3: The Council / Socials
                Div(
                    H4("THE COUNCIL", cls="text-xs font-heading font-bold tracking-[0.2em] text-[#D4AF37] mb-4 uppercase"),
                    Ul(
                        Li(A("Ali Kazem (@shadowurameshi)", href="https://instagram.com/shadowurameshi", target="_blank", rel="noopener noreferrer", cls="text-xs text-neutral-400 hover:text-[#D4AF37] transition-colors")),
                        Li(A("Malik Rose (@gentlemanrosayy)", href="https://instagram.com/gentlemanrosayy", target="_blank", rel="noopener noreferrer", cls="text-xs text-neutral-400 hover:text-[#D4AF37] transition-colors")),
                        Li(A("Unkn0wn (@unkn0wndaproducer)", href="https://instagram.com/unkn0wndaproducer", target="_blank", rel="noopener noreferrer", cls="text-xs text-neutral-400 hover:text-[#D4AF37] transition-colors")),
                        Li(A("Yung Illie (@illieaking)", href="https://instagram.com/illieaking", target="_blank", rel="noopener noreferrer", cls="text-xs text-neutral-400 hover:text-[#D4AF37] transition-colors")),
                        cls="space-y-2.5 list-none p-0 m-0"
                    ),
                    cls="flex flex-col"
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-10"
            ),
            # Bottom Bar
            Div(
                Div(
                    P("© 2026 UNICORN BOUNTY HUNTERS. ALL RIGHTS RESERVED.", cls="text-[11px] text-neutral-500 font-mono"),
                    P("POWERED BY FASTHTML • DATASTAR • GOOGLE CLOUD RUN", cls="text-[10px] text-[#D4AF37]/70 font-mono tracking-widest"),
                    cls="flex flex-col md:flex-row items-center justify-between gap-4"
                ),
                cls="border-t border-[#1A1A1A] mt-12 pt-8"
            ),
            cls="max-w-7xl mx-auto px-6 py-14"
        ),
        cls="w-full bg-[#050505] border-t border-[#1A1A1A] mt-auto"
    )
