# Codebase Audit & Security Vulnerability Report

**Project:** Unicorn Bounty Hunter (UBH) — FastHTML + Datastar + Firebase + Stripe Platform
**Architecture:** Python 3.12+, FastHTML, Datastar (v1.x SSE), Firebase Firestore, Stripe API
**Scope:** Full static code analysis across `main.py`, `config.py`, `routes/`, `services/`, `components/`, `firestore.rules`, `storage.rules`, and test scripts.

---

## 1. Executive Summary

A comprehensive security and code quality audit was performed on the **Unicorn Bounty Hunter (UBH)** web application repository. The application is built using Python, FastHTML, Datastar (v1.x Server-Sent Events), Firebase Firestore, and Stripe for studio session bookings, content management, and live event promotions.

The audit revealed critical security vulnerabilities, authentication weaknesses, payment bypass opportunities, and operational bugs.

---

## 2. Vulnerability Findings & Security Risks

### 🔴 CRITICAL SEVERITY

#### 1. Hardcoded Admin Secret Key & Information Disclosure Prior to Authentication
* **Location:** `config.py` (Line 31) & `routes/admin.py` (Line 64)
* **Description:**
  * The default fallback secret key `shadowurameshi2026` is hardcoded in `config.py` when `ADMIN_SECRET_KEY` / `ADMIN_KEY` environment variables are not supplied.
  * In `routes/admin.py` inside `get_admin()`, when an unauthenticated request hits `/admin` without a `key` query parameter, the function queries and loads sensitive database records (subscriber emails, events, showcases, artist posts) **before** verifying if the user is authenticated:
    ```python
    slots = get_all_slots_for_date_admin(date)
    events = get_events()
    showcases = get_showcases()
    subscribers = get_subscribers() # Subscriber emails fetched before auth check!
    all_posts = get_all_artist_posts()
    ```
* **Impact:** Potential admin portal takeover if environment variables are missing in deployment. Subscriber emails and unauthenticated data are unnecessarily fetched into memory.
* **Remediation:** Remove hardcoded fallback secret keys or raise an exception on startup if unconfigured. Perform authentication checks before querying sensitive backend collections.

#### 2. Stripe Webhook Signature Verification Bypass & Mock Payload Spoofing
* **Location:** `services/stripe_service.py` (Lines 102–115) & `routes/booking.py` (Lines 279–310)
* **Description:**
  * In `verify_webhook_event()`, if `STRIPE_WEBHOOK_SECRET` is not set or starts with `whsec_mock`, the application skips official signature verification and parses raw JSON directly:
    ```python
    try:
        import json
        return json.loads(payload.decode("utf-8"))
    except Exception:
        return None
    ```
  * In `routes/booking.py`, POST `/booking/webhook` accepts unverified webhooks in mock/dev configurations and updates studio booking slots to `booked` status automatically.
* **Impact:** Anyone can craft a POST request to `/booking/webhook` with arbitrary JSON to lock out studio slots without making a real payment.
* **Remediation:** Enforce strict Stripe webhook signature verification (`stripe.Webhook.construct_event`) in production environments.

#### 3. CSRF & Credential Leak via URL Query Parameters
* **Location:** `routes/admin.py` (Lines 435–446)
* **Description:**
  * Admin endpoints such as `/admin/slots/delete` accept secret keys in URL parameters or form data without session management or CSRF tokens.
  * The admin key is passed in URL query strings across navigation links (e.g. `<a href="/admin?key=shadowurameshi2026&tab=posts">`).
* **Impact:** Secret admin keys leak in HTTP `Referer` headers (when navigating to embedded YouTube links or external ticket URLs), server logs, and browser history. Anyone with the link can perform admin actions.
* **Remediation:** Transition from query-parameter authentication to HTTP-only session cookies and implement CSRF token protection for state-changing POST requests.

---

### 🟠 HIGH SEVERITY

#### 4. Payment Simulation Endpoint Exposed in Production Mode
* **Location:** `routes/booking.py` (Lines 91–198)
* **Description:**
  * Routes `/booking/mock-checkout` and `/booking/mock-complete` are continuously mounted and accessible.
  * A user can directly call `/booking/mock-complete` with a target `slot_id` to reserve studio time without going through Stripe.
* **Impact:** Direct financial bypass allowing unauthorized booking of studio time.
* **Remediation:** Disable or guard mock payment endpoints behind an explicit development environment flag (e.g. `if os.getenv("ENVIRONMENT") != "development"`).

#### 5. Unchecked Authorization & Input Validation on Admin Deletion Endpoints
* **Location:** `routes/admin.py` (Lines 519–531)
* **Description:**
  * `post_admin_artist_post_delete` processes post deletion requests with minimal validation on `post_id`.
* **Impact:** Potential unauthorized or erroneous content deletion.
* **Remediation:** Add sanitization, existence checks, and strict validation on resource IDs before deletion operations.

---

### 🟡 MEDIUM SEVERITY

#### 6. Unrestricted YouTube URL Extraction / Improper Sanitization
* **Location:** `routes/admin.py` (Lines 35–62)
* **Description:**
  * `extract_youtube_id()` processes pasted YouTube URLs using regex. If an invalid input is passed, it returns `(raw, False)`, storing raw unsanitized strings in Firestore as `youtube_id`.
* **Impact:** Storing invalid YouTube IDs breaks the frontend iframe player component (`components/player.py`).
* **Remediation:** Strictly validate YouTube IDs (must be exactly 11 characters matching `[a-zA-Z0-9_-]{11}` or a valid playlist ID).

#### 7. Missing Protocol Sanitization on External Media URLs
* **Location:** `components/artist_profile.py` & `routes/admin.py`
* **Description:**
  * User-supplied URLs for `media_url`, `flyer_url`, and `ticket_url` are rendered directly into HTML attributes (`<img src="...">`, `<a href="...">`).
* **Impact:** Potential Cross-Site Scripting (XSS) or injection via `javascript:` pseudoprotocols if malicious URLs are submitted.
* **Remediation:** Validate that media and external links strictly start with `http://`, `https://`, or allowed relative paths (`/static/`).

---

### 🔵 LOW SEVERITY & OPERATIONAL BUGS

#### 8. Broken Test Suite Dependencies and Live Server Assumptions
* **Location:** `test_app.py`, `test_admin_delete_and_calendar.py`, `test_artist_routes.py`, `test_checkout_flow.py`, `test_events_and_rap_funxtion.py`
* **Description:**
  * Running `pytest` results in errors due to missing dependencies (`starlette`) in `test_app.py` and `ConnectionRefusedError: [Errno 111]` across other test scripts which expect a live server listening on `http://localhost:8000`.
* **Impact:** CI/CD pipeline test execution will fail by default.
* **Remediation:** Refactor unit and integration tests to use Starlette/FastAPI `TestClient` or `httpx.AsyncClient` in-process rather than depending on external running servers.

#### 9. Absence of Rate Limiting on Public POST Endpoints
* **Location:** `routes/public.py` (`/subscribe`) & `routes/booking.py` (`/booking/create-checkout`)
* **Description:**
  * `/subscribe` and checkout creation endpoints lack rate limiting or CAPTCHA validation.
* **Impact:** Vulnerable to automated submission spam or rate-limit exhaustion.
* **Remediation:** Implement rate-limiting middleware (such as `slowapi` or standard memory token buckets).

---

## 3. Summary Matrix of Audit Findings

| ID | Issue Title | Target Location | Severity | Category |
|---|---|---|---|---|
| **1** | Hardcoded Key & Pre-Auth Data Leak | `config.py`, `routes/admin.py` | 🔴 Critical | Authentication |
| **2** | Webhook Signature Verification Bypass | `services/stripe_service.py`, `routes/booking.py` | 🔴 Critical | Payment Integrity |
| **3** | Admin Key Exposure in URLs & CSRF Risk | `routes/admin.py` | 🔴 Critical | Session Security |
| **4** | Mock Payment Route Exposed in Production | `routes/booking.py` | 🟠 High | Business Logic |
| **5** | Unvalidated Content Deletion Handler | `routes/admin.py` | 🟠 High | Access Control |
| **6** | Unsanitized YouTube ID Extraction | `routes/admin.py` | 🟡 Medium | Input Validation |
| **7** | Unsanitized Protocol in Media URLs | `components/artist_profile.py` | 🟡 Medium | XSS Prevention |
| **8** | Test Suite Failures & Socket Requirements | `test_*.py` | 🔵 Low / Bug | CI/CD & Testing |
| **9** | Missing Rate Limiting on Public Endpoints | `routes/public.py`, `routes/booking.py` | 🔵 Low | Anti-Spam |
