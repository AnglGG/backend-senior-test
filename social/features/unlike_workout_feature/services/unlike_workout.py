"""Service: remove the caller's like on a completed training session."""

from social.models import WorkoutLike
from users.models import User


def unlike_workout(*, user: User, workout_session_id: int) -> None:
    WorkoutLike.objects.filter(user=user, workout_session_id=workout_session_id).delete()
