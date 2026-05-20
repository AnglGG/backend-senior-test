"""Service: register a user's like on a completed training session."""

from social.models import WorkoutLike
from users.models import User


def like_workout(*, user: User, workout_session_id: int) -> WorkoutLike:
    return WorkoutLike.objects.create(user=user, workout_session_id=workout_session_id)
