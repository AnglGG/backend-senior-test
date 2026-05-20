"""API: POST /workouts/{workout_id}/comments/

Adds a comment authored by the requesting user. 404 if the session does not
exist or the viewer is not allowed to see it.
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from social.features.add_workout_comment_feature.services import (
    add_workout_comment,
)
from workout_sessions.core.services import can_view_workout
from workout_sessions.models import WorkoutSession

from .add_workout_comment_serializers import (
    AddWorkoutCommentInputSerializer,
    AddWorkoutCommentOutputSerializer,
)


class AddWorkoutCommentView(APIView):
    @extend_schema(
        request=AddWorkoutCommentInputSerializer,
        responses={201: AddWorkoutCommentOutputSerializer},
    )
    def post(self, request: Request, workout_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        workout_session = get_object_or_404(WorkoutSession, pk=workout_id)
        if not can_view_workout(viewer=request.user, workout_session=workout_session):
            raise NotFound()

        serializer = AddWorkoutCommentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = add_workout_comment(
            user=request.user,
            workout_session_id=workout_id,
            body=serializer.validated_data["body"],
        )

        return Response(
            AddWorkoutCommentOutputSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )
