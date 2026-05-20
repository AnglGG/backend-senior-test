"""URL routes for the `users` app.

Mounted at `/users/`. Some endpoints (follow/unfollow, list-followers,
list-following, list-user-workout-plans, list-user-workouts) have views
that live in `social.features.*`, `workout_plans.features.*` or
`workout_sessions.features.*` but are mounted here because the resource is
the user.
"""

from django.urls import path

from social.features.follow_user_feature.api.follow_user_api import (
    FollowUserView,
)
from social.features.list_followers_feature.api.list_followers_api import (
    ListFollowersView,
)
from social.features.list_following_feature.api.list_following_api import (
    ListFollowingView,
)
from social.features.unfollow_user_feature.api.unfollow_user_api import (
    UnfollowUserView,
)
from users.features.get_my_profile_feature.api.get_my_profile_api import (
    GetMyProfileView,
)
from users.features.update_my_preferences_feature.api.update_my_preferences_api import (
    UpdateMyPreferencesView,
)
from workout_plans.features.list_user_workout_plans_feature.api.list_user_workout_plans_api import (
    ListUserWorkoutPlansView,
)
from workout_sessions.features.list_user_workouts_feature.api.list_user_workouts_api import (
    ListUserWorkoutsView,
)

app_name = "users"

urlpatterns = [
    path("me/", GetMyProfileView.as_view(), name="me"),
    path("me/preferences/", UpdateMyPreferencesView.as_view(), name="update_preferences"),
    path("<int:target_user_id>/follow/", FollowUserView.as_view(), name="follow"),
    path("<int:target_user_id>/unfollow/", UnfollowUserView.as_view(), name="unfollow"),
    path("<int:user_id>/followers/", ListFollowersView.as_view(), name="list_followers"),
    path("<int:user_id>/following/", ListFollowingView.as_view(), name="list_following"),
    path("<int:user_id>/workout-plans/", ListUserWorkoutPlansView.as_view(), name="list_workout_plans"),
    path("<int:user_id>/workouts/", ListUserWorkoutsView.as_view(), name="list_workouts"),
]
