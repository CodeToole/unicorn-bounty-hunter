from fasthtml.common import *

def EmailCaptureModal():
    return Div(
        Div(
            Div(
                # Close button
                Button(
                    "✕",
                    onclick="document.getElementById('email-capture-modal').style.display='none'",
                    cls="absolute top-4 right-4 text-neutral-400 hover:text-white text-lg font-bold bg-transparent border-0 cursor-pointer"
                ),
                # Insignia
                Div(
                    Span("⚡", cls="text-2xl mb-1 block"),
                    Span("JOIN THE HUNT", cls="text-xs font-heading font-bold tracking-[0.4em] text-[#D4AF37] uppercase block"),
                    H3("VIP ROSTER ACCESS", cls="text-2xl md:text-3xl font-black font-heading tracking-tight text-white uppercase mt-1"),
                    P("Subscribe for instant alerts on Rap Funxtion tickets, studio lock drops, and limited-edition collective uniform drops.", cls="text-neutral-400 text-xs md:text-sm mt-2 max-w-xs mx-auto leading-relaxed"),
                    cls="text-center mb-6"
                ),
                # Form
                Form(
                    Div(
                        Input(
                            type="email",
                            name="email",
                            placeholder="ENTER YOUR EMAIL ADDRESS",
                            required=True,
                            id="modal-email-input",
                            cls="input-dark w-full text-center text-xs md:text-sm font-heading tracking-wider mb-3"
                        ),
                        Button(
                            "CLAIM ACCESS",
                            type="submit",
                            cls="btn-gold w-full text-xs font-heading font-black tracking-widest py-3"
                        ),
                        Div(id="modal-subscribe-status", cls="text-center text-xs mt-3"),
                        cls="flex flex-col"
                    ),
                    onsubmit="""
                        event.preventDefault();
                        const emailInput = document.getElementById('modal-email-input');
                        const statusDiv = document.getElementById('modal-subscribe-status');
                        statusDiv.innerHTML = '<span class=\"text-[#D4AF37]\">ENCRYPTING & SUBMITTING...</span>';
                        fetch('/subscribe', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                            body: 'email=' + encodeURIComponent(emailInput.value)
                        }).then(res => res.json()).then(data => {
                            if (data.success) {
                                statusDiv.innerHTML = '<span class=\"text-emerald-400 font-bold font-heading\">WELCOME TO THE ROSTER.</span>';
                                emailInput.value = '';
                                setTimeout(() => { document.getElementById('email-capture-modal').style.display='none'; }, 2000);
                            } else {
                                statusDiv.innerHTML = '<span class=\"text-rose-400\">' + (data.error || 'Submission failed.') + '</span>';
                            }
                        }).catch(e => {
                            statusDiv.innerHTML = '<span class=\"text-rose-400\">Network error.</span>';
                        });
                    """
                ),
                cls="relative bg-[#0D0D0D] border border-[#D4AF37]/40 rounded-2xl max-w-md w-full p-8 shadow-2xl gold-glow"
            ),
            cls="min-h-screen flex items-center justify-center p-4"
        ),
        id="email-capture-modal",
        cls="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm hidden"
    )

def EmailCaptureWidget():
    return Div(
        # Floating toggle button
        Div(
            Div(
                # Pop-up drawer
                Div(
                    H4("GET UBH EXCLUSIVES", cls="text-xs font-heading font-bold text-[#D4AF37] tracking-wider uppercase mb-1"),
                    P("Enter your email for priority studio and show drop alerts:", cls="text-[11px] text-neutral-400 mb-3"),
                    Form(
                        Input(
                            type="email",
                            name="email",
                            placeholder="YOUR EMAIL",
                            required=True,
                            id="widget-email-input",
                            cls="input-dark w-full text-xs py-2 px-3 mb-2 font-body"
                        ),
                        Button(
                            "SUBSCRIBE",
                            type="submit",
                            cls="btn-gold w-full text-xs py-2 tracking-widest font-heading font-black"
                        ),
                        Div(id="widget-subscribe-status", cls="text-xs mt-2 text-center"),
                        onsubmit="""
                            event.preventDefault();
                            const emailInput = document.getElementById('widget-email-input');
                            const statusDiv = document.getElementById('widget-subscribe-status');
                            statusDiv.innerHTML = '<span class=\"text-[#D4AF37]\">Submitting...</span>';
                            fetch('/subscribe', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                                body: 'email=' + encodeURIComponent(emailInput.value)
                            }).then(res => res.json()).then(data => {
                                if (data.success) {
                                    statusDiv.innerHTML = '<span class=\"text-emerald-400 font-bold\">Subscribed!</span>';
                                    emailInput.value = '';
                                } else {
                                    statusDiv.innerHTML = '<span class=\"text-rose-400\">' + (data.error || 'Failed') + '</span>';
                                }
                            }).catch(e => {
                                statusDiv.innerHTML = '<span class=\"text-rose-400\">Error</span>';
                            });
                        """
                    ),
                    id="email-widget-drawer",
                    cls="hidden mb-3 bg-[#0D0D0D] border border-[#D4AF37]/40 rounded-xl p-5 w-72 md:w-80 shadow-2xl text-left"
                ),
                Button(
                    Span("✉️", cls="text-xl"),
                    onclick="""
                        const drawer = document.getElementById('email-widget-drawer');
                        drawer.classList.toggle('hidden');
                    """,
                    cls="w-12 h-12 md:w-14 md:h-14 bg-[#D4AF37] hover:bg-[#FFD700] text-black rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-105 duration-200 cursor-pointer border-0 ml-auto"
                ),
                cls="flex flex-col items-end"
            ),
            cls="fixed bottom-6 right-6 z-40"
        ),
        id="email-widget-container"
    )
