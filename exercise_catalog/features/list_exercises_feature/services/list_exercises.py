"""Service: list exercise templates.

The catalog is read-mostly: the same set of `ExerciseTemplate` rows is fetched
on nearly every screen, and the underlying data only changes when an admin
edits the catalog. That makes this a natural place to cache by filter
combination. Results are materialized so the view can paginate in Python
against a cached list.
"""

from django.core.cache import cache

from exercise_catalog.models import ExerciseTemplate


# Five minutes is a fair trade between catalog freshness and load on the
# read path. Bump the version suffix when the response shape changes.
_CACHE_KEY_PREFIX = "exercises:v1"
_CACHE_TTL_SECONDS = 60 * 5


def list_exercises(
    *,
    muscle_group: str | None = None,
    equipment: str | None = None,
    search: str | None = None,
) -> list[ExerciseTemplate]:
    cache_key = f"{_CACHE_KEY_PREFIX}:{muscle_group}:{equipment}:{search}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    queryset = ExerciseTemplate.objects.all()
    if muscle_group:
        queryset = queryset.filter(primary_muscle_group=muscle_group)
    if equipment:
        queryset = queryset.filter(equipment=equipment)
    if search:
        queryset = queryset.filter(name__icontains=search)

    result = list(queryset)
    cache.set(cache_key, result, timeout=_CACHE_TTL_SECONDS)
    return result
