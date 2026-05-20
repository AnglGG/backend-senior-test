"""Service: fetch a workout plan with its routines (days) and exercises prefetched."""

from django.db.models import Prefetch

from workout_plans.models import Routine, RoutineExercise, WorkoutPlan


def get_workout_plan_details(workout_plan_id: int) -> WorkoutPlan | None:
    try:
        return (
            WorkoutPlan.objects
            .prefetch_related(
                Prefetch(
                    "routines",
                    queryset=Routine.objects.order_by("day_index").prefetch_related(
                        Prefetch(
                            "exercises",
                            queryset=RoutineExercise.objects
                            .select_related("exercise_template")
                            .order_by("position"),
                        )
                    ),
                )
            )
            .get(pk=workout_plan_id)
        )
    except WorkoutPlan.DoesNotExist:
        return None
