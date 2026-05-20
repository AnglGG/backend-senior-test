"""URL routes for the `workout_sessions` app.

Mounted at `/workouts/`. The workout resource is the natural place to attach
social interactions (likes, comments) even though their views live in
`social.features.*`, so this file imports across bounded contexts.
"""

from django.urls import path

from social.features.add_workout_comment_feature.api.add_workout_comment_api import (
    AddWorkoutCommentView,
)
from social.features.like_workout_feature.api.like_workout_api import (
    LikeWorkoutView,
)
from social.features.list_workout_comments_feature.api.list_workout_comments_api import (
    ListWorkoutCommentsView,
)
from social.features.unlike_workout_feature.api.unlike_workout_api import (
    UnlikeWorkoutView,
)
from workout_sessions.features.create_workout_feature.api.create_workout_api import (
    CreateWorkoutView,
)
from workout_sessions.features.delete_workout_feature.api.delete_workout_api import (
    DeleteWorkoutView,
)
from workout_sessions.features.get_workout_details_feature.api.get_workout_details_api import (
    GetWorkoutDetailsView,
)
from workout_sessions.features.update_workout_feature.api.update_workout_api import (
    UpdateWorkoutView,
)

app_name = "workout_sessions"

urlpatterns = [
    path("", CreateWorkoutView.as_view(), name="create"),
    path("<int:workout_id>/", GetWorkoutDetailsView.as_view(), name="details"),
    path("<int:workout_id>/update/", UpdateWorkoutView.as_view(), name="update"),
    path("<int:workout_id>/delete/", DeleteWorkoutView.as_view(), name="delete"),
    path("<int:workout_id>/like/", LikeWorkoutView.as_view(), name="like"),
    path("<int:workout_id>/unlike/", UnlikeWorkoutView.as_view(), name="unlike"),
    path("<int:workout_id>/comments/", ListWorkoutCommentsView.as_view(), name="list_comments"),
    path("<int:workout_id>/comments/add/", AddWorkoutCommentView.as_view(), name="add_comment"),
]
