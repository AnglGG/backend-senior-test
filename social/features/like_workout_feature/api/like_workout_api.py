"""API: POST /workouts/{workout_id}/like/

Registers a like authored by the requesting user on a completed training session.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from social.features.like_workout_feature.services import like_workout
from workout_sessions.core.services import can_view_workout
from workout_sessions.models import WorkoutSession

from .like_workout_serializers import LikeWorkoutOutputSerializer


class LikeWorkoutView(APIView):
    def post(self, request: Request, workout_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        workout_session = get_object_or_404(WorkoutSession, pk=workout_id)
        if not can_view_workout(viewer=request.user, workout_session=workout_session):
            raise NotFound()

        workout_like = like_workout(
            user=request.user, workout_session_id=workout_id
        )

        return Response(
            LikeWorkoutOutputSerializer({
                "user": {
                    "id": request.user.id,
                    "display_name": request.user.display_name,
                    "avatar_url": request.user.avatar_url,
                },
                "created_at": workout_like.created_at,
            }).data,
            status=status.HTTP_201_CREATED,
        )
