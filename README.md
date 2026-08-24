# Unicorn Bounty Hunter (UBH) — Official Collective & Studio Platform

![Python 3.14](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![FastHTML](https://img.shields.io/badge/Framework-FastHTML-gold)
![Datastar](https://img.shields.io/badge/Reactivity-Datastar_SSE-black)
![Firebase](https://img.shields.io/badge/Database-Firebase_Firestore-FFCA28?logo=firebase)
![GCP Cloud Run](https://img.shields.io/badge/Deployment-Google_Cloud_Run-4285F4?logo=googlecloud)

Production web platform for Unicorn Bounty Hunter (UBH), featuring interactive studio session booking with time locks, an executive CMS engine, dynamic artist profiles, news carousels, and live Stripe payment processing.

---

## 🚀 Tech Stack

- **Backend**: Python 3.14 + FastHTML (ASGI / Starlette)
- **Frontend Reactivity**: Datastar (Server-Sent Events)
- **Database**: Firebase Firestore (Dual-mode live & local store)
- **Payments**: Stripe Hosted Checkout API
- **Containerization**: Docker (`linux/amd64`)
- **Infrastructure**: Google Cloud Run (`us-central1`)
- **Hosting Proxy**: Firebase Hosting (`ubh-production-2026.web.app`)

---

## ⚡ Key Features

- **Interactive Studio Booking Schedule**: Date selector dropdown with real-time SSE time-lock slots (e.g. 4-Hour $200 Locks) to prevent double-booking. Includes package toggles for Studio Recording and Shadow Talk Podcast sessions.
- **Executive CMS Portal (`/admin`)**: Password-protected portal for managing studio availability, resetting test bookings, managing event flyers, and reviewing email mailing list subscribers.
- **Artist Creator Portal & Profiles**: Dynamic roster pages (`/roster/{artist_slug}`) with individual article publishing, CMS post deletion, YouTube embeds, and mobile social sharing toolbars (Web Share API, X, Facebook, Copy Link).
- **Homepage News Carousel**: "LATEST FROM THE HUNT" ticker displaying recent dispatches directly on the homepage.
- **Rap Funxtion Showcase**: Live event management system initialized to "Coming Soon" with dynamic flyer uploads.

---

## 📁 Repository Structure

```text
.
├── components/          # FastHTML hypermedia components (Calendar, Roster, Profiles, Carousel)
├── routes/              # Endpoints (public.py, booking.py, admin.py, sse.py)
├── services/            # Firestore database handlers and Stripe Checkout session manager
├── static/              # Production CSS design system (theme.css), images, and brand assets
├── config.py            # Environment configurations & secret management
├── main.py              # Server entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # Multi-stage container file with dynamic $PORT binding
├── firebase.json        # Firebase Hosting rewrite rules targeting Cloud Run
└── firestore.rules      # Firestore security rules
```

---

## 🛠️ Local Development

### 1. Prerequisites
- Python 3.14+
- (Optional) Google Cloud SDK & Firebase CLI

### 2. Environment Setup
Create a `.env` file in the root directory:
```bash
STRIPE_SECRET_KEY=sk_live_...
ADMIN_SECRET_KEY=your_secure_admin_passcode
PORT=8000
DOMAIN_URL=http://localhost:8000
```

### 3. Install Dependencies & Run
```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # On Windows

# Install packages
pip install -r requirements.txt

# Start the FastHTML engine
python main.py
```
Visit `http://localhost:8000` in your browser.

### 4. Administrative Access
- Console URL: `/admin` (e.g. `http://localhost:8000/admin`)
- Passcode: Configured via environment variable `ADMIN_SECRET_KEY`

---

## 🧪 Testing

Run the automated integration test suite:
```bash
python -m unittest test_app.py
python test_artist_routes.py
python test_events_and_rap_funxtion.py
python test_admin_delete_and_calendar.py
```

---

## 🚢 Deployment

### Firebase Hosting & Rules
```bash
firebase deploy --only firestore:rules,hosting --project ubh-production-2026
```

### Google Cloud Run Container Build
```bash
gcloud builds submit --tag gcr.io/ubh-production-2026/ubh-python-app
gcloud run deploy ubh-python-app \
  --image gcr.io/ubh-production-2026/ubh-python-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
