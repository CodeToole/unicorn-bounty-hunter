import os
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

# Server & Domain Config
PORT = int(os.getenv("PORT", "8000"))
DOMAIN_URL = os.getenv("DOMAIN_URL", "http://localhost:8000").rstrip("/")

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key_ubh_2026")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_key_ubh_2026")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_mock_key_ubh_2026")

# Admin Security
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", os.getenv("ADMIN_KEY", "[REDACTED_ADMIN_SECRET]"))
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
