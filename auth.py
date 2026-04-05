"""
Shared authentication module for NXTIER.

Provides verify_pin() with:
  - Supabase-backed PIN verification (replaces Google Sheets lookup)
  - bcrypt comparison (PINs stored hashed in clients.pin_hash)
  - 5-minute in-memory cache to avoid repeated DB round-trips
"""
import time
from typing import Optional
from passlib.hash import bcrypt as bcrypt_hash

from database import supabase


# ── In-memory PIN cache ────────────────────────────────────────────────────────
# Structure: { client_id: (pin_hash, expires_at) }
_cache: dict[str, tuple[str, float]] = {}
_CACHE_TTL = 300  # 5 minutes


def _get_cached_hash(client_id: str) -> Optional[str]:
    entry = _cache.get(client_id)
    if entry and time.time() < entry[1]:
        return entry[0]
    _cache.pop(client_id, None)
    return None


def _set_cached_hash(client_id: str, pin_hash: str) -> None:
    _cache[client_id] = (pin_hash, time.time() + _CACHE_TTL)


# ── Public API ─────────────────────────────────────────────────────────────────
def verify_pin(client_id: str, pin: str) -> bool:
    """
    Returns True if the given plain-text pin matches the stored bcrypt hash
    for this client_id. Results are cached for 5 minutes.
    """
    # 1. Try cache first
    cached = _get_cached_hash(client_id)
    if cached is not None:
        return bcrypt_hash.verify(pin, cached)

    # 2. Hit Supabase
    try:
        res = (
            supabase.table("clients")
            .select("pin_hash")
            .eq("id", client_id)
            .single()
            .execute()
        )
        if not res.data:
            return False
        pin_hash = res.data["pin_hash"]
        _set_cached_hash(client_id, pin_hash)
        return bcrypt_hash.verify(pin, pin_hash)
    except Exception:
        return False


def get_client(client_id: str) -> Optional[dict]:
    """
    Returns the full client row from Supabase, or None if not found.
    Used by admin login to get business_name, email, etc.
    """
    try:
        res = (
            supabase.table("clients")
            .select("id, business_name, email, pin_hash")
            .eq("id", client_id)
            .single()
            .execute()
        )
        return res.data or None
    except Exception:
        return None


def invalidate_cache(client_id: str) -> None:
    """Call this after a PIN change to force re-verification."""
    _cache.pop(client_id, None)
