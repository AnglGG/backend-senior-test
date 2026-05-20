"""Visibility rules shared across workout-session read paths.

The app is a private social network: a workout is readable by its owner and
by anyone who follows the owner. There is no per-workout `visibility` setting
and no notion of a public account. Centralising the rule keeps every read
endpoint asking the same question.
"""

from social.models import Following
from users.models import User
from workout_sessions.models import WorkoutSession


def can_view_workout(*, viewer: User, workout_session: WorkoutSession) -> bool:
    """Return True when `viewer` is allowed to read `workout_session`.

    Owners always see their own sessions. Any other authenticated viewer needs
    an existing `Following` row pointing from themselves to the owner.
    """

    if not viewer.is_authenticated:
        return False

    if workout_session.user_id == viewer.id:
        return True

    return Following.objects.filter(
        follower=viewer,
        followed_id=workout_session.user_id,
    ).exists()
