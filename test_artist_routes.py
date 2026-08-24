import sys
from starlette.testclient import TestClient
from main import app
from routes.admin import get_session_token

client = TestClient(app)
client.cookies.set("ubh_admin_session", get_session_token())

print("=" * 60)
print("UBH ARTIST ROUTES INTEGRATION TEST (IN-MEMORY)")
print("=" * 60)

routes = [
    "/",
    "/roster",
    "/roster/ali-kazem",
    "/roster/malik-rose",
    "/roster/unkn0wn",
    "/roster/yung-illie",
    "/roster/nonexistent-artist",
    "/admin?tab=posts",
]

fails = 0
for path in routes:
    resp = client.get(path)
    status = resp.status_code
    tag = "OK" if status == 200 else "FAIL"
    if status != 200:
        fails += 1
    print("  %s  [%s] %s" % (tag, status, path))

print("=" * 60)

# Publish a test post for Ali Kazem to test full card rendering & toolbar
client.post("/admin/posts/add", data={
    "artist_slug": "ali-kazem",
    "title": "Studio Field Report",
    "body": "Tracking sessions live in the acoustic room with new HS8 monitoring setup.",
    "media_url": ""
}, follow_redirects=False)

# Content checks on Ali Kazem profile
resp = client.get("/roster/ali-kazem")
html = resp.text
checks = [
    ("Ali Kazem name in page", "ALI KAZEM" in html),
    ("Instagram handle link", "shadowurameshi" in html),
    ("Post title rendered", "Studio Field Report" in html),
    ("Web Share API in toolbar", "navigator.share" in html),
    ("Clipboard copy in toolbar", "navigator.clipboard" in html),
    ("Back to roster link", "BACK TO ROSTER" in html),
]
print("\nProfile content checks (ali-kazem):")
for label, passed in checks:
    tag = "OK" if passed else "FAIL"
    if not passed:
        fails += 1
    print("  %s  %s" % (tag, label))

# Admin Creator Portal checks
resp2 = client.get("/admin?tab=posts")
html2 = resp2.text
admin_checks = [
    ("Creator Portal heading", "ARTIST CREATOR PORTAL" in html2),
    ("Artist slug selector", "artist_slug" in html2),
    ("Publish button", "PUBLISH POST" in html2),
    ("Delete post button", "Delete Post" in html2),
]
print("\nAdmin Creator Portal checks:")
for label, passed in admin_checks:
    tag = "OK" if passed else "FAIL"
    if not passed:
        fails += 1
    print("  %s  %s" % (tag, label))

print("\n" + "=" * 60)
if fails == 0:
    print("RESULT: ALL TESTS PASSED")
else:
    print("RESULT: %d FAILURES" % fails)
print("=" * 60)

sys.exit(0 if fails == 0 else 1)
