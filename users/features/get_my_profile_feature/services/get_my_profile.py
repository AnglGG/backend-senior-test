"""Service: fetch the requesting user's full profile.

The `UserProfile` slice of the response is cached forever and refreshed only
through the `post_save` signal on `UserProfile` (see
`users.core.services.profile_cache` and `users.signals`). The rest of the
response — identity fields on `User` and the joined active workout plan — is
fetched fresh from the database on every call.
"""

from django.db.models import Prefetch

from users.core.services.profile_cache import (
    build_profile_summary,
    cache_profile_summary,
    get_cached_profile_summary,
)
from users.models import User
from workout_plans.models import UserActiveWorkoutPlan


def get_my_profile(user: User) -> dict:
    cached_profile = get_cached_profile_summary(user_id=user.pk)

    if cached_profile is not None:
        user_row = (
            User.objects
            .prefetch_related(
                Prefetch(
                    "active_workout_plan",
                    queryset=UserActiveWorkoutPlan.objects.select_related(
                        "workout_plan"
                    ),
                )
            )
            .get(pk=user.pk)
        )
        profile_summary = cached_profile
    else:
        user_row = (
            User.objects
            .select_related("profile")
            .prefetch_related(
                Prefetch(
                    "active_workout_plan",
                    queryset=UserActiveWorkoutPlan.objects.select_related(
                        "workout_plan"
                    ),
                )
            )
            .get(pk=user.pk)
        )
        profile = getattr(user_row, "profile", None)
        profile_summary = build_profile_summary(profile) if profile else None
        if profile_summary is not None:
            cache_profile_summary(user_id=user.pk, summary=profile_summary)

    return {
        "id": user_row.id,
        "username": user_row.username,
        "display_name": user_row.display_name,
        "avatar_url": user_row.avatar_url,
        "bio": user_row.bio,
        "profile": profile_summary,
        "active_workout_plan": _serialize_active_plan(
            getattr(user_row, "active_workout_plan", None)
        ),
    }


def _serialize_active_plan(active) -> dict | None:
    if active is None:
        return None
    return {
        "workout_plan_id": active.workout_plan.id,
        "workout_plan_name": active.workout_plan.name,
        "current_day_index": active.current_day_index,
        "started_at": active.started_at,
    }
