"""Service: list a user's completed training sessions, newest first."""

from django.db.models import QuerySet

from workout_sessions.models import WorkoutSession


def list_user_workouts(
    *,
    target_user_id: int,
    offset: int = 0,
    limit: int = 20,
) -> QuerySet[WorkoutSession]:
    """Return the target user's completed training sessions, newest first.

    Slicing is applied in the service so the caller does not have to evaluate
    the queryset itself.
    """
    return (
        WorkoutSession.objects
        .filter(user_id=target_user_id)
        .order_by("-started_at")
        [offset : offset + limit]
    )
