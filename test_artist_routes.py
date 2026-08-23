"""Quick integration test for all new artist routes (Windows-safe)."""
import urllib.request
import sys

BASE = "http://localhost:8000"

def test_route(path):
    try:
        resp = urllib.request.urlopen(BASE + path, timeout=5)
        return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)

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

print("=" * 60)
print("UBH ARTIST ROUTES INTEGRATION TEST")
print("=" * 60)

fails = 0
for path in routes:
    status = test_route(path)
    tag = "OK" if status == 200 else "FAIL"
    if status != 200:
        fails += 1
    print("  %s  [%s] %s" % (tag, status, path))

print("=" * 60)

# Content checks on Ali Kazem profile
resp = urllib.request.urlopen(BASE + "/roster/ali-kazem", timeout=5)
html = resp.read().decode("utf-8", errors="replace")
checks = [
    ("Ali Kazem name in page", "ALI KAZEM" in html),
    ("Instagram handle link", "shadowurameshi" in html),
    ("Seed post title present", "Rap Funxtion 16" in html),
    ("Web Share API in toolbar", "navigator.share" in html),
    ("Clipboard copy in toolbar", "navigator.clipboard" in html),
    ("X/Twitter share link", "x.com/intent/tweet" in html),
    ("Facebook share link", "facebook.com/sharer" in html),
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
    ("Seed post visible", "Rap Funxtion 16" in html2),
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
sys.exit(1 if fails else 0)
