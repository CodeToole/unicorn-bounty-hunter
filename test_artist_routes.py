import urllib.request
import urllib.parse
import json
import sys

BASE = "http://localhost:8000"

def test_route(path):
    try:
        req = urllib.request.Request(BASE + path, headers={"User-Agent": "UBH-Test"})
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)

print("=" * 60)
print("UBH ARTIST ROUTES INTEGRATION TEST")
print("=" * 60)

routes = [
    "/",
    "/roster",
    "/roster/ali-kazem",
    "/roster/malik-rose",
    "/roster/unkn0wn",
    "/roster/yung-illie",
    "/roster/nonexistent-artist",
    "/admin?key=shadowurameshi2026&tab=posts",
]

fails = 0
for path in routes:
    status = test_route(path)
    tag = "OK" if status == 200 else "FAIL"
    if status != 200:
        fails += 1
    print("  %s  [%s] %s" % (tag, status, path))

print("=" * 60)

# Publish a test post for Ali Kazem to test full card rendering & toolbar
post_data = urllib.parse.urlencode({
    "key": "shadowurameshi2026",
    "artist_slug": "ali-kazem",
    "title": "Studio Field Report",
    "body": "Tracking sessions live in the acoustic room with new HS8 monitoring setup.",
    "media_url": ""
}).encode("utf-8")
req_post = urllib.request.Request(BASE + "/admin/posts/add", data=post_data, method="POST")
urllib.request.urlopen(req_post, timeout=5)

# Content checks on Ali Kazem profile
resp = urllib.request.urlopen(BASE + "/roster/ali-kazem", timeout=5)
html = resp.read().decode("utf-8", errors="replace")
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
resp2 = urllib.request.urlopen(BASE + "/admin?key=shadowurameshi2026&tab=posts", timeout=5)
html2 = resp2.read().decode("utf-8", errors="replace")
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
