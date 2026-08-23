from fasthtml.common import *
import datetime
from typing import List, Dict, Any

def _render_package_selector(disabled: bool = False):
    return Div(
        Label("1. CHOOSE SERVICE / PACKAGE:", cls="block text-xs font-heading font-bold text-[#D4AF37] tracking-wider mb-3 uppercase"),
        Div(
            # Studio Recording Option
            Label(
                Input(
                    type="radio",
                    name="package_type",
                    value="studio",
                    checked=True,
                    disabled=disabled,
                    cls="hidden peer"
                ),
                Div(
                    Div(
                        Div(
                            Span("🎙️", cls="text-lg mr-2"),
                            Span("Studio Recording Session", cls="font-heading font-bold text-sm text-white"),
                            cls="flex items-center"
                        ),
                        Span("$50/HR (Time Locks)", cls="text-[11px] font-mono font-bold text-[#D4AF37] bg-[#1F1F1F] px-2 py-0.5 rounded border border-[#333]"),
                        cls="flex items-center justify-between mb-1"
                    ),
                    P("Vocal tracking, Pro Tools session, vocal auto-tune chain & raw WAV stems.", cls="text-neutral-400 text-xs leading-relaxed"),
                    cls="p-3.5 bg-[#141414] border border-[#262626] rounded-xl peer-checked:border-[#D4AF37] peer-checked:bg-[#D4AF37]/10 cursor-pointer transition-all hover:border-[#D4AF37]/60"
                ),
                cls="block cursor-pointer"
            ),
            # Shadow Talk Podcast Standard Option
            Label(
                Input(
                    type="radio",
                    name="package_type",
                    value="podcast_standard",
                    disabled=disabled,
                    cls="hidden peer"
                ),
                Div(
                    Div(
                        Div(
                            Span("📻", cls="text-lg mr-2"),
                            Span("Shadow Talk Podcast (Standard)", cls="font-heading font-bold text-sm text-white"),
                            cls="flex items-center"
                        ),
                        Span("$50 FLAT (1-HR)", cls="text-[11px] font-mono font-bold text-[#D4AF37] bg-[#1F1F1F] px-2 py-0.5 rounded border border-[#333]"),
                        cls="flex items-center justify-between mb-1"
                    ),
                    P("1-Hour in-depth interview broadcast with 4-mic setup & 4K multi-camera video.", cls="text-neutral-400 text-xs leading-relaxed"),
                    cls="p-3.5 bg-[#141414] border border-[#262626] rounded-xl peer-checked:border-[#D4AF37] peer-checked:bg-[#D4AF37]/10 cursor-pointer transition-all hover:border-[#D4AF37]/60"
                ),
                cls="block cursor-pointer"
            ),
            # Shadow Talk Podcast + Musical Chairs Bundle Option
            Label(
                Input(
                    type="radio",
                    name="package_type",
                    value="podcast_bundle",
                    disabled=disabled,
                    cls="hidden peer"
                ),
                Div(
                    Div(
                        Div(
                            Span("👑", cls="text-lg mr-2"),
                            Span("Podcast + Musical Chairs Bundle", cls="font-heading font-bold text-sm text-white"),
                            cls="flex items-center"
                        ),
                        Span("$100 BUNDLE SPECIAL", cls="text-[11px] font-mono font-bold text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-600/50"),
                        cls="flex items-center justify-between mb-1"
                    ),
                    P("Full podcast episode interview + featured spot on the official Musical Chairs cypher.", cls="text-neutral-400 text-xs leading-relaxed"),
                    cls="p-3.5 bg-[#141414] border border-[#262626] rounded-xl peer-checked:border-[#D4AF37] peer-checked:bg-[#D4AF37]/10 cursor-pointer transition-all hover:border-[#D4AF37]/60"
                ),
                cls="block cursor-pointer"
            ),
            cls="space-y-2.5 mb-6"
        )
    )

def BookingCalendar(selected_date: str = "", slots: List[Dict[str, Any]] = None):
    if not selected_date:
        selected_date = datetime.date.today().isoformat()
    if slots is None:
        slots = []

    today_str = datetime.date.today().isoformat()

    return Div(
        Div(
            # Header
            Div(
                Span("RESERVE STUDIO & BROADCAST TIME", cls="text-xs font-heading font-bold tracking-[0.3em] text-[#D4AF37] uppercase block mb-1"),
                H2("FACILITY SCHEDULE & BOOKING", cls="text-2xl md:text-3xl font-black font-heading tracking-tight text-white uppercase mb-2"),
                P("Select your creative package and lock in engineer availability. Real-time slot verification with instant confirmation.", cls="text-neutral-400 text-xs md:text-sm max-w-lg mb-6"),
                cls="text-center md:text-left"
            ),
            # Date Picker Control with Datastar SSE event trigger
            Div(
                Label("SELECT SESSION DATE:", cls="block text-xs font-heading font-bold text-neutral-300 tracking-wider mb-2"),
                Input(
                    type="date",
                    id="booking-date",
                    name="booking_date",
                    value=selected_date,
                    min=today_str,
                    # Datastar SSE trigger: dynamically calls SSE endpoint on change to stream updated slots
                    data_on_change="$$get('/sse/available-slots')",
                    data_bind="booking_date",
                    cls="bg-[#121212] border border-[#2A2A2A] focus:border-[#D4AF37] text-white p-3.5 rounded-lg w-full outline-none font-body text-sm transition-all focus:ring-1 focus:ring-[#D4AF37]"
                ),
                cls="mb-6",
                id="calendar-controls"
            ),
            # Slot Container targeted by Datastar SSE merge-fragments
            Div(
                RenderSlotOptions(slots, selected_date=selected_date),
                id="slot-container",
                cls="datastar-transition"
            ),
            cls="p-6 md:p-8 bg-[#0D0D0D] border border-[#1F1F1F] rounded-2xl max-w-2xl mx-auto shadow-2xl"
        ),
        id="studio-booking-widget",
        cls="w-full py-8"
    )

def RenderSlotOptions(slots: List[Dict[str, Any]], selected_date: str = ""):
    if not slots:
        return Div(
            _render_package_selector(disabled=True),
            Div(
                Span("⚠️", cls="text-3xl mb-2 block"),
                H4("No Available Slots for Selected Date", cls="text-white font-heading font-bold text-base mb-1"),
                P(f"All recording locks are booked or blocked for {selected_date}. Please select another date on the calendar above.", cls="text-neutral-400 text-xs max-w-sm mx-auto"),
                cls="text-center py-8 px-4 bg-[#121212] border border-[#222222] rounded-xl mb-4"
            ),
            id="slot-container"
        )

    return Form(
        # 1. Creative Package Selector Toggle
        _render_package_selector(disabled=False),
        # 2. Slot selection grid
        Div(
            Label("2. SELECT AVAILABLE TIME LOCK:", cls="block text-xs font-heading font-bold text-[#D4AF37] tracking-wider mb-3 uppercase"),
            Div(
                *[
                    Label(
                        Input(
                            type="radio",
                            name="slot_id",
                            value=slot["id"],
                            required=True,
                            cls="hidden peer"
                        ),
                        Div(
                            Div(
                                Span(slot["time_label"], cls="font-heading font-bold text-sm md:text-base text-white block group-hover:text-[#D4AF37] transition-colors"),
                                Span(f"{slot.get('duration', 2)} Hour Block ({selected_date})", cls="text-[11px] text-neutral-400 font-body block mt-0.5"),
                                cls="flex flex-col"
                            ),
                            Div(
                                Span(f"${slot.get('price', 100)} USD", cls="text-xs md:text-sm font-mono font-bold text-[#D4AF37] bg-[#1A1A1A] border border-[#333333] px-2.5 py-1 rounded"),
                                cls="ml-auto"
                            ),
                            cls="p-4 bg-[#141414] border border-[#262626] rounded-xl peer-checked:border-[#D4AF37] peer-checked:bg-[#D4AF37]/10 cursor-pointer transition-all hover:border-[#D4AF37]/60 flex items-center justify-between shadow-sm"
                        ),
                        cls="block cursor-pointer"
                    )
                    for slot in slots
                ],
                cls="space-y-3 mb-6"
            )
        ),
        # Hidden date input
        Input(type="hidden", name="requested_date", value=selected_date),
        # 3. Contact & Artist Details
        Div(
            Label("3. ARTIST & BOOKING CONTACT:", cls="block text-xs font-heading font-bold text-[#D4AF37] tracking-wider mb-3 uppercase"),
            Div(
                Input(
                    type="text",
                    name="artist_name",
                    placeholder="Artist / Group / Producer / Guest Name *",
                    required=True,
                    cls="input-dark w-full text-sm font-body mb-3"
                ),
                Input(
                    type="email",
                    name="artist_email",
                    placeholder="Contact Email Address (for confirmation) *",
                    required=True,
                    cls="input-dark w-full text-sm font-body mb-3"
                ),
                Input(
                    type="tel",
                    name="phone_number",
                    placeholder="Phone Number (SMS Session Reminders)",
                    cls="input-dark w-full text-sm font-body mb-4"
                ),
                Textarea(
                    name="session_notes",
                    placeholder="Session Goals / Notes (e.g. vocal tracking, podcast topic, mix review)...",
                    rows="3",
                    cls="input-dark w-full text-sm font-body mb-6"
                ),
                cls="flex flex-col"
            )
        ),
        # Submit Button
        Button(
            Span("PROCEED TO SECURE STRIPE CHECKOUT", cls="font-heading font-extrabold tracking-widest text-xs md:text-sm"),
            Span("🔒 256-BIT ENCRYPTION • INSTANT CONFIRMATION", cls="text-[10px] font-mono text-black/75 block mt-0.5 tracking-wider"),
            type="submit",
            cls="w-full bg-[#D4AF37] hover:bg-[#FFD700] text-black py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-[#D4AF37]/20 cursor-pointer text-center flex flex-col items-center justify-center font-heading"
        ),
        action="/booking/create-checkout",
        method="POST",
        id="slot-container"
    )
