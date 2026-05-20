"""Service: fetch a completed training session with everything a detail view needs.

Performs the single query (with `select_related` + nested `Prefetch`) that
materializes the session, its exercises in order, each exercise's sets in
order, the linked exercise templates, and the social counts. Returns `None`
when the session does not exist; the caller decides how to surface that
(usually 404).
"""

from django.db.models import Count, Prefetch

from workout_sessions.models import (
    WorkoutSession,
    WorkoutSessionExercise,
    WorkoutSessionSet,
)


def get_workout_details(workout_id: int) -> WorkoutSession | None:
    try:
        return _build_queryset().get(pk=workout_id)
    except WorkoutSession.DoesNotExist:
        return None


def _build_queryset():
    return WorkoutSession.objects.select_related("user").annotate(
        like_count=Count("likes", distinct=True),
        comment_count=Count("comments", distinct=True),
    ).prefetch_related(
        Prefetch(
            "exercises",
            queryset=WorkoutSessionExercise.objects.select_related(
                "exercise_template"
            ).order_by("position").prefetch_related(
                Prefetch(
                    "sets",
                    queryset=WorkoutSessionSet.objects.order_by("position"),
                )
            ),
        ),
    )
