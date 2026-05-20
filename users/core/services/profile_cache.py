"""Profile summary cache.

`GET /users/me/` sits on the home-screen hot path: every cold start of the
app calls it. The `UserProfile` fields it surfaces (experience level, primary
goal, training frequency, available equipment, etc.) change rarely compared
to how often they are read, so we cache them indefinitely.

Freshness is **signal-driven**: a `post_save` handler on `UserProfile` (see
`users.signals`) invalidates the entry whenever a profile row is saved, and
the next read recomputes from the database. There is intentionally no TTL —
the cache lives forever until the signal (or an explicit invalidation) drops
the entry.
"""

from django.core.cache import cache

from users.models import UserProfile


CACHE_KEY_TEMPLATE = "profile_summary:{user_id}"


def get_cached_profile_summary(*, user_id: int) -> dict | None:
    return cache.get(CACHE_KEY_TEMPLATE.format(user_id=user_id))


def cache_profile_summary(*, user_id: int, summary: dict) -> None:
    # `timeout=None` stores the entry without expiry. Refresh is the
    # `post_save` signal's job.
    cache.set(
        CACHE_KEY_TEMPLATE.format(user_id=user_id),
        summary,
        timeout=None,
    )


def invalidate_profile_summary(*, user_id: int) -> None:
    cache.delete(CACHE_KEY_TEMPLATE.format(user_id=user_id))


def build_profile_summary(profile: UserProfile) -> dict:
    """Project a `UserProfile` row to the dict shape we cache and serialize."""
    return {
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "date_of_birth": profile.date_of_birth,
        "experience_level": profile.experience_level,
        "primary_goal": profile.primary_goal,
        "training_frequency_per_week": profile.training_frequency_per_week,
        "available_equipment": profile.available_equipment,
    }
