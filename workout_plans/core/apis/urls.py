"""URL routes for the `workout_plans` app.

Mounted at `/workout-plans/`. The endpoints scoped to a specific user
(listing their plans, setting an active plan) are registered from
`users.core.apis.urls` instead, because their resource is the user.
"""

from django.urls import path

from workout_plans.features.create_workout_plan_feature.api.create_workout_plan_api import (
    CreateWorkoutPlanView,
)
from workout_plans.features.get_workout_plan_details_feature.api.get_workout_plan_details_api import (
    GetWorkoutPlanDetailsView,
)

app_name = "workout_plans"

urlpatterns = [
    path("", CreateWorkoutPlanView.as_view(), name="create"),
    path("<int:workout_plan_id>/", GetWorkoutPlanDetailsView.as_view(), name="details"),
]
