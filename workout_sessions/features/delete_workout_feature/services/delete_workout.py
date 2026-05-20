"""Service: delete a workout session (cascading down to exercises and sets)."""

from workout_sessions.models import WorkoutSession


def delete_workout(*, workout_session: WorkoutSession) -> None:
    workout_session.delete()
