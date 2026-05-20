"""Service: list the workout plans a user owns, newest first."""

from django.db.models import QuerySet

from workout_plans.models import WorkoutPlan


def list_user_workout_plans(*, user_id: int) -> QuerySet[WorkoutPlan]:
    return WorkoutPlan.objects.filter(user_id=user_id).order_by("-created_at")
