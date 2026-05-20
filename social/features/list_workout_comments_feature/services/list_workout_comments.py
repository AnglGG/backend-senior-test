"""Service: list comments on a completed training session, oldest first."""

from django.db.models import QuerySet

from social.models import WorkoutComment


def list_workout_comments(*, workout_session_id: int) -> QuerySet[WorkoutComment]:
    return WorkoutComment.objects.filter(
        workout_session_id=workout_session_id
    ).order_by("created_at")
