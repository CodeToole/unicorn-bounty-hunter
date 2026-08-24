import os
import datetime
from typing import List, Dict, Optional, Any
from config import FIREBASE_STORAGE_BUCKET, DEFAULT_TIME_SLOTS

# Attempt Firebase Admin SDK initialization
_firestore_db = None
_storage_bucket = None
_is_firebase_initialized = False

# Only initialize live Firebase SDK if in Cloud Run, GAE, or if credentials path is explicitly set
_has_explicit_creds = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and os.path.exists(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")))
_is_cloud_env = bool(os.getenv("K_SERVICE") or os.getenv("GAE_ENV") or os.getenv("GCP_PROJECT"))

if _has_explicit_creds or _is_cloud_env:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, storage

        if not firebase_admin._apps:
            try:
                if _has_explicit_creds:
                    cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
                else:
                    cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'storageBucket': FIREBASE_STORAGE_BUCKET
                })
                _firestore_db = firestore.client()
                _storage_bucket = storage.bucket()
                _is_firebase_initialized = True
                print("Firebase Admin SDK initialized successfully.")
            except Exception as auth_err:
                print(f"Firebase initialization bypassed ({auth_err}). Running in local fallback mode.")
        else:
            _firestore_db = firestore.client()
            _is_firebase_initialized = True
    except Exception as e:
        print(f"Firebase Admin SDK not loaded ({e}). Operating in standalone fallback mode.")
else:
    print("Operating in local dual-mode with fast in-memory and local asset store.")

# Local In-Memory Fallback Storage
_local_slots: Dict[str, List[Dict[str, Any]]] = {}
_local_subscribers: List[Dict[str, Any]] = [
    {"email": "ali@shadowurameshi.com", "created_at": "2026-08-20T10:00:00Z"},
    {"email": "hunt@unicornbountyhunters.com", "created_at": "2026-08-22T14:30:00Z"}
]
_local_events: List[Dict[str, Any]] = [
    {
        "id": "rf-coming-soon",
        "title": "Rap Funxtion",
        "date": "Coming Soon",
        "status": "Coming Soon",
        "flyer_url": "/static/assets/rf16_flyer_new.jpg",
        "ticket_url": "#",
        "active": True,
        "description": "New dates, venue details, and lineup configurations are currently being finalized. Stay tuned for official announcements."
    }
]
_local_showcases: List[Dict[str, Any]] = [
    {
        "id": "mc-series",
        "title": "Musical Chairs Series",
        "youtube_id": "videoseries?list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1",
        "is_playlist": True,
        "description": "Official UBH Musical Chairs Cypher & Showcase Playlist",
        "created_at": "2026-08-01T00:00:00Z"
    }
]

# Helper to generate default slots for a given date
def _generate_default_slots_for_date(date_str: str) -> List[Dict[str, Any]]:
    slots = []
    for idx, template in enumerate(DEFAULT_TIME_SLOTS):
        slots.append({
            "id": f"{date_str}-{template['id']}",
            "date": date_str,
            "time_label": template["time_label"],
            "duration": template["duration"],
            "price": template["price"],
            "status": "available",  # 'available', 'booked', 'blocked'
            "artist_name": None,
            "artist_email": None
        })
    return slots

# ----------------- Booking Slots -----------------

def get_slots_for_date(date_str: Optional[str]) -> List[Dict[str, Any]]:
    if not date_str:
        date_str = datetime.date.today().isoformat()

    if _is_firebase_initialized and _firestore_db:
        try:
            docs = _firestore_db.collection("booking_slots").where("date", "==", date_str).stream()
            results = [doc.to_dict() | {"id": doc.id} for doc in docs]
            if results:
                return results
            # If no slots exist yet for date in Firestore, seed defaults
            defaults = _generate_default_slots_for_date(date_str)
            for s in defaults:
                _firestore_db.collection("booking_slots").document(s["id"]).set(s)
            return defaults
        except Exception as err:
            print(f"Firestore slot query failed: {err}. Falling back to local store.")

    # Local fallback
    if date_str not in _local_slots:
        _local_slots[date_str] = _generate_default_slots_for_date(date_str)
    return [s for s in _local_slots[date_str] if s["status"] == "available"]

def get_all_slots_for_date_admin(date_str: Optional[str]) -> List[Dict[str, Any]]:
    if not date_str:
        date_str = datetime.date.today().isoformat()

    if _is_firebase_initialized and _firestore_db:
        try:
            docs = _firestore_db.collection("booking_slots").where("date", "==", date_str).stream()
            results = [doc.to_dict() | {"id": doc.id} for doc in docs]
            if results:
                return results
            defaults = _generate_default_slots_for_date(date_str)
            for s in defaults:
                _firestore_db.collection("booking_slots").document(s["id"]).set(s)
            return defaults
        except Exception as err:
            print(f"Firestore admin slot query failed: {err}")

    if date_str not in _local_slots:
        _local_slots[date_str] = _generate_default_slots_for_date(date_str)
    return _local_slots[date_str]

def get_slot_by_id(slot_id: str) -> Optional[Dict[str, Any]]:
    if not slot_id:
        return None

    if _is_firebase_initialized and _firestore_db:
        try:
            doc = _firestore_db.collection("booking_slots").document(slot_id).get()
            if doc.exists:
                return doc.to_dict() | {"id": doc.id}
        except Exception as err:
            print(f"Firestore get slot error: {err}")

    for date_slots in _local_slots.values():
        for s in date_slots:
            if s["id"] == slot_id:
                return s
    
    # Check if id format is date-slot-x
    parts = slot_id.rsplit("-slot-", 1)
    if len(parts) == 2:
        date_str = parts[0]
        if date_str not in _local_slots:
            _local_slots[date_str] = _generate_default_slots_for_date(date_str)
        for s in _local_slots[date_str]:
            if s["id"] == slot_id:
                return s
    return None

def update_slot_status(
    slot_id: str,
    status: str,
    artist_name: Optional[str] = None,
    artist_email: Optional[str] = None,
    package_type: Optional[str] = None,
    package_name: Optional[str] = None
) -> bool:
    data = {
        "status": status,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    if artist_name is not None:
        data["artist_name"] = artist_name
    if artist_email is not None:
        data["artist_email"] = artist_email
    if package_type is not None:
        data["package_type"] = package_type
    if package_name is not None:
        data["package_name"] = package_name

    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("booking_slots").document(slot_id).update(data)
            return True
        except Exception as err:
            print(f"Firestore update slot error: {err}")

    slot = get_slot_by_id(slot_id)
    if slot:
        slot.update(data)
        return True
    return False

def reset_slot_booking(slot_id: str) -> bool:
    """Reset a slot back to 'available' and clear all customer/artist reservation metadata."""
    data = {
        "status": "available",
        "artist_name": None,
        "artist_email": None,
        "phone_number": None,
        "session_notes": None,
        "package_type": None,
        "package_name": None,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("booking_slots").document(slot_id).set(data, merge=True)
            return True
        except Exception as err:
            print(f"Firestore reset slot error: {err}")

    slot = get_slot_by_id(slot_id)
    if slot:
        slot["status"] = "available"
        slot.pop("artist_name", None)
        slot.pop("artist_email", None)
        slot.pop("phone_number", None)
        slot.pop("session_notes", None)
        slot.pop("package_type", None)
        slot.pop("package_name", None)
        slot["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return True
    return False

# ----------------- Subscribers -----------------

def add_subscriber(email: str) -> bool:
    email = email.strip().lower()
    if not email or "@" not in email:
        return False

    sub_data = {
        "email": email,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("subscribers").document(email).set(sub_data)
            return True
        except Exception as err:
            print(f"Firestore add subscriber error: {err}")

    # Local fallback
    if not any(s["email"] == email for s in _local_subscribers):
        _local_subscribers.append(sub_data)
    return True

def get_subscribers() -> List[Dict[str, Any]]:
    if _is_firebase_initialized and _firestore_db:
        try:
            docs = _firestore_db.collection("subscribers").order_by("created_at", direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as err:
            print(f"Firestore get subscribers error: {err}")
    return sorted(_local_subscribers, key=lambda x: x.get("created_at", ""), reverse=True)

# ----------------- Events -----------------

def get_events() -> List[Dict[str, Any]]:
    if _is_firebase_initialized and _firestore_db:
        try:
            docs = _firestore_db.collection("events").stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as err:
            print(f"Firestore get events error: {err}")
    return _local_events

def add_event(title: str, date: str, status: str, flyer_url: str, ticket_url: str, description: str) -> Dict[str, Any]:
    event_id = f"event-{int(datetime.datetime.now().timestamp())}"
    data = {
        "id": event_id,
        "title": title,
        "date": date,
        "status": status,
        "flyer_url": flyer_url or "/static/assets/rf16_flyer_new.jpg",
        "ticket_url": ticket_url or "#",
        "active": True,
        "description": description,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("events").document(event_id).set(data)
            return data
        except Exception as err:
            print(f"Firestore add event error: {err}")

    _local_events.insert(0, data)
    return data

def delete_event(event_id: str) -> bool:
    """Delete an event by ID from Firestore and local store."""
    global _local_events
    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("events").document(event_id).delete()
            return True
        except Exception as err:
            print(f"Firestore delete event error: {err}")

    original_len = len(_local_events)
    _local_events = [e for e in _local_events if e.get("id") != event_id]
    return len(_local_events) < original_len

# ----------------- YouTube Showcases -----------------

def get_showcases() -> List[Dict[str, Any]]:
    if _is_firebase_initialized and _firestore_db:
        try:
            docs = _firestore_db.collection("showcases").order_by("created_at", direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as err:
            print(f"Firestore get showcases error: {err}")
    return _local_showcases

def add_showcase(title: str, youtube_id: str, description: str, is_playlist: bool = False) -> Dict[str, Any]:
    showcase_id = f"showcase-{int(datetime.datetime.now().timestamp())}"
    data = {
        "id": showcase_id,
        "title": title,
        "youtube_id": youtube_id,
        "is_playlist": is_playlist,
        "description": description,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("showcases").document(showcase_id).set(data)
            return data
        except Exception as err:
            print(f"Firestore add showcase error: {err}")

    _local_showcases.insert(0, data)
    return data

# ----------------- Artist Posts -----------------

_local_artist_posts: List[Dict[str, Any]] = []

def delete_artist_post(post_id: str) -> bool:
    """Delete an artist post by ID from Firestore collection 'artist_posts' and clear from local cache."""
    global _local_artist_posts
    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("artist_posts").document(post_id).delete()
        except Exception as err:
            print(f"Firestore delete artist_post error: {err}")

    original_len = len(_local_artist_posts)
    _local_artist_posts = [p for p in _local_artist_posts if p.get("id") != post_id]
    return True

def get_artist_posts(artist_slug: str) -> List[Dict[str, Any]]:
    """Get all published posts for a given artist slug, sorted by created_at descending."""
    if _is_firebase_initialized and _firestore_db:
        try:
            docs = (
                _firestore_db.collection("artist_posts")
                .where("artist_slug", "==", artist_slug)
                .where("published", "==", True)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .stream()
            )
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as err:
            print(f"Firestore get artist_posts error: {err}")

    # Local fallback
    posts = [p for p in _local_artist_posts if p["artist_slug"] == artist_slug and p.get("published", True)]
    return sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)

def get_recent_artist_posts(limit: int = 5) -> List[Dict[str, Any]]:
    """Query the most recent published artist posts from Firestore collection 'artist_posts'."""
    if _is_firebase_initialized and _firestore_db:
        try:
            docs = (
                _firestore_db.collection("artist_posts")
                .where("published", "==", True)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as err:
            print(f"Firestore get recent artist_posts error: {err}")

    posts = [p for p in _local_artist_posts if p.get("published", True)]
    sorted_posts = sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)
    return sorted_posts[:limit]

def get_all_artist_posts() -> List[Dict[str, Any]]:
    """Get all published posts across all artists."""
    if _is_firebase_initialized and _firestore_db:
        try:
            docs = (
                _firestore_db.collection("artist_posts")
                .where("published", "==", True)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .stream()
            )
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as err:
            print(f"Firestore get all artist_posts error: {err}")

    posts = [p for p in _local_artist_posts if p.get("published", True)]
    return sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)

def add_artist_post(artist_slug: str, title: str, body: str, media_url: str = "") -> Dict[str, Any]:
    """Create a new artist post and persist it."""
    post_id = f"post-{artist_slug}-{int(datetime.datetime.now().timestamp())}"
    data = {
        "id": post_id,
        "artist_slug": artist_slug,
        "title": title.strip(),
        "body": body.strip(),
        "media_url": media_url.strip() if media_url else "",
        "published": True,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("artist_posts").document(post_id).set(data)
            return data
        except Exception as err:
            print(f"Firestore add artist_post error: {err}")

    _local_artist_posts.insert(0, data)
    return data


# ----------------- Multi-Tenant User Accounts & RBAC -----------------

_local_user_accounts: List[Dict[str, Any]] = []

def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_user_account(email: str, password: str, role: str = "artist_admin", artist_slug: str = "") -> Dict[str, Any]:
    email = email.strip().lower()
    data = {
        "email": email,
        "password_hash": hash_password(password),
        "role": role,
        "artist_slug": artist_slug if role == "artist_admin" else "",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("user_accounts").document(email).set(data)
            return data
        except Exception as err:
            print(f"Firestore create user_account error: {err}")

    # Local fallback
    existing = [u for u in _local_user_accounts if u["email"] == email]
    if existing:
        existing[0].update(data)
    else:
        _local_user_accounts.append(data)
    return data

def authenticate_user_account(email: str, password: str) -> Optional[Dict[str, Any]]:
    email = email.strip().lower()
    pw_hash = hash_password(password)

    if _is_firebase_initialized and _firestore_db:
        try:
            doc = _firestore_db.collection("user_accounts").document(email).get()
            if doc.exists:
                user = doc.to_dict()
                if user.get("password_hash") == pw_hash:
                    return user
        except Exception as err:
            print(f"Firestore authenticate user error: {err}")

    # Local fallback
    for u in _local_user_accounts:
        if u["email"] == email and u.get("password_hash") == pw_hash:
            return u
    return None

def get_all_user_accounts() -> List[Dict[str, Any]]:
    if _is_firebase_initialized and _firestore_db:
        try:
            docs = _firestore_db.collection("user_accounts").stream()
            return [doc.to_dict() for doc in docs]
        except Exception as err:
            print(f"Firestore get user_accounts error: {err}")
    return _local_user_accounts

# ----------------- Customizable Slot & Bulk Wipe System -----------------

def add_custom_slot_for_date(date_str: str, time_label: str, duration: int, price: int) -> Dict[str, Any]:
    """Create a new custom booking slot for a specific date."""
    slot_id = f"{date_str}-custom-{int(datetime.datetime.now().timestamp())}"
    data = {
        "id": slot_id,
        "date": date_str,
        "time_label": time_label,
        "duration": duration,
        "price": price,
        "status": "available",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("booking_slots").document(slot_id).set(data)
            return data
        except Exception as err:
            print(f"Firestore add custom slot error: {err}")

    # Local store
    slots = _local_slots.setdefault(date_str, [])
    slots.append(data)
    return data

def delete_all_slots_for_date(date_str: str) -> bool:
    """Wipe / delete all booking slots for a specific date."""
    if _is_firebase_initialized and _firestore_db:
        try:
            docs = _firestore_db.collection("booking_slots").where("date", "==", date_str).stream()
            for doc in docs:
                doc.reference.delete()
        except Exception as err:
            print(f"Firestore delete all slots for date error: {err}")

    _local_slots[date_str] = []
    return True

def block_entire_day_for_date(date_str: str) -> bool:
    """Clear existing slots and block the entire day with a 'Maintenance / Closed' slot."""
    delete_all_slots_for_date(date_str)
    block_id = f"{date_str}-blocked"
    data = {
        "id": block_id,
        "date": date_str,
        "time_label": "ALL DAY BLOCK (Studio Closed / Maintenance)",
        "duration": 24,
        "price": 0,
        "status": "maintenance",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    if _is_firebase_initialized and _firestore_db:
        try:
            _firestore_db.collection("booking_slots").document(block_id).set(data)
            return True
        except Exception as err:
            print(f"Firestore block entire day error: {err}")

    _local_slots[date_str] = [data]
    return True
