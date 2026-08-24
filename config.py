import os
import secrets
from pathlib import Path

# Load .env file automatically if present
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_file)
    except ImportError:
        # Built-in fallback .env reader
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'").strip('"')
                    os.environ[k] = v

# Environment & Mode
ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()
IS_PRODUCTION = (ENVIRONMENT == "production")

# Server & Domain Config
PORT = int(os.getenv("PORT", "8000"))
DOMAIN_URL = os.getenv("DOMAIN_URL", "http://localhost:8000").rstrip("/")

# Stripe Configuration
if IS_PRODUCTION:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
else:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key_ubh_2026")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_key_ubh_2026")
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_mock_key_ubh_2026")

def is_live_stripe_enabled() -> bool:
    """Returns True if a real / live Stripe secret key is configured."""
    key = STRIPE_SECRET_KEY.strip() if STRIPE_SECRET_KEY else ""
    return bool(key and not key.startswith("sk_test_mock") and not key.startswith("placeholder"))

def is_mock_payment_allowed() -> bool:
    """Mock checkout is strictly disabled in production mode or when live Stripe keys exist."""
    return not IS_PRODUCTION and not is_live_stripe_enabled()

# Admin Security
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", os.getenv("ADMIN_KEY", ""))
if not ADMIN_SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError("ADMIN_SECRET_KEY environment variable must be set in production mode.")
    else:
        ADMIN_SECRET_KEY = "[REDACTED_ADMIN_SECRET]"

ADMIN_KEY = ADMIN_SECRET_KEY

# Firebase Configuration
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "ubh-production-2026.appspot.com")
FIREBASE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# Studio Booking Pricing ($50/hour base)
HOURLY_RATE = 50
DEFAULT_TIME_SLOTS = [
    {"id": "slot-1", "time_label": "12:00 PM – 2:00 PM (2 Hours)", "duration": 2, "price": 100},
    {"id": "slot-2", "time_label": "2:30 PM – 4:30 PM (2 Hours)", "duration": 2, "price": 100},
    {"id": "slot-3", "time_label": "5:00 PM – 7:00 PM (2 Hours)", "duration": 2, "price": 100},
    {"id": "slot-4", "time_label": "7:30 PM – 9:30 PM (2 Hours)", "duration": 2, "price": 100},
    {"id": "slot-5", "time_label": "10:00 PM – 2:00 AM (4-Hour Lock)", "duration": 4, "price": 200},
]
