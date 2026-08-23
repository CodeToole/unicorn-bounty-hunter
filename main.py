import os
from fasthtml.common import *
from starlette.staticfiles import StaticFiles

# Import Route apps
from routes.public import public_app
from routes.booking import booking_app
from routes.admin import admin_app
from routes.sse import sse_app
from config import PORT

# Ensure static directories exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/assets", exist_ok=True)
os.makedirs("static/videos", exist_ok=True)

# Initialize FastHTML Master Application
app, rt = fast_app(
    live=False,
    pwa=False,
    hdrs=(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1, maximum-scale=1"),
        # Google Fonts
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;900&display=swap"),
        # Tailwind CSS
        Script(src="https://cdn.tailwindcss.com"),
        # Datastar Hypermedia Engine CDN (v1.x beta)
        Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-beta.1/bundles/datastar.js"),
        # UBH Theme Styles
        Link(rel="stylesheet", href="/static/css/theme.css"),
    )
)

# Merge route handlers from modular route applications
app.routes.extend(public_app.routes)
app.routes.extend(booking_app.routes)
app.routes.extend(admin_app.routes)
app.routes.extend(sse_app.routes)

# Mount Static File Server
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health Check for Cloud Run & load balancers
@rt("/health")
def get_health():
    return "OK"

if __name__ == "__main__":
    import uvicorn
    print(f"Starting UBH FastHTML Engine on port {PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
