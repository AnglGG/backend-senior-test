"""Service: fetch one `ExerciseTemplate` with its aliases prefetched."""

from django.db.models import Prefetch

from exercise_catalog.models import ExerciseTemplate, ExerciseTemplateAlias


def get_exercise_by_id(exercise_id: int) -> ExerciseTemplate | None:
    try:
        return (
            ExerciseTemplate.objects
            .prefetch_related(
                Prefetch(
                    "aliases",
                    queryset=ExerciseTemplateAlias.objects.order_by("locale", "name"),
                )
            )
            .get(pk=exercise_id)
        )
    except ExerciseTemplate.DoesNotExist:
        return None
