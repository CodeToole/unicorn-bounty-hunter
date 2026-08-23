from fasthtml.common import *
from starlette.responses import StreamingResponse
from components.calendar import RenderSlotOptions
from components.artist_profile import _post_card
from services.firebase_service import get_slots_for_date, get_artist_posts
import datetime
import json

sse_app = FastHTML()
rt = sse_app.route

@rt("/sse/available-slots")
async def get_available_slots(req):
    # Extract requested date from query parameters or datastar signals
    date = req.query_params.get("booking_date") or req.query_params.get("date")
    if not date and "datastar" in req.query_params:
        try:
            signal_data = json.loads(req.query_params["datastar"])
            date = signal_data.get("booking_date") or signal_data.get("date")
        except Exception:
            pass

    if not date:
        date = datetime.date.today().isoformat()

    slots = get_slots_for_date(date)
    fragment_html = to_xml(RenderSlotOptions(slots, selected_date=date))

    async def event_generator():
        # Datastar v1.x beta merge-fragments protocol
        # Targets elements by id (e.g. #slot-container)
        sse_event = f"event: datastar-merge-fragments\ndata: fragments {fragment_html}\n\n"
        yield sse_event.encode("utf-8")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@rt("/sse/artist-posts/{artist_slug}")
async def get_artist_posts_sse(artist_slug: str):
    """SSE endpoint for real-time artist post feed updates via Datastar."""
    posts = get_artist_posts(artist_slug)

    # Build fragment HTML for the feed container
    feed_items = Div(
        *[_post_card(post, idx) for idx, post in enumerate(posts)],
        id=f"artist-feed-{artist_slug}",
        cls="space-y-5"
    )
    fragment_html = to_xml(feed_items)

    async def event_generator():
        sse_event = f"event: datastar-merge-fragments\ndata: fragments {fragment_html}\n\n"
        yield sse_event.encode("utf-8")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
