"""URL routes for the `exercise_catalog` app.

Mounted at `/exercises/`. Routes are declared here and import each feature's
`APIView`.
"""

from django.urls import path

from exercise_catalog.features.get_exercise_by_id_feature.api.get_exercise_by_id_api import (
    GetExerciseByIdView,
)
from exercise_catalog.features.list_exercises_feature.api.list_exercises_api import (
    ListExercisesView,
)

app_name = "exercise_catalog"

urlpatterns = [
    path("", ListExercisesView.as_view(), name="list"),
    path("<int:exercise_id>/", GetExerciseByIdView.as_view(), name="details"),
]
