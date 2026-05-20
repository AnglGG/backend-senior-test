"""API: POST /workouts/

Creates a workout owned by the requesting user. All persistence is delegated
to the service; this layer only handles HTTP concerns.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workout_sessions.features.create_workout_feature.services import create_workout

from .create_workout_serializers import (
    CreateWorkoutInputSerializer,
    CreateWorkoutOutputSerializer,
)


class CreateWorkoutView(APIView):
    @extend_schema(
        request=CreateWorkoutInputSerializer,
        responses={201: CreateWorkoutOutputSerializer},
    )
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        serializer = CreateWorkoutInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workout_session = create_workout(
            user=request.user,
            payload=serializer.to_domain_input(),
        )

        output = CreateWorkoutOutputSerializer({"id": workout_session.id})
        return Response(output.data, status=status.HTTP_201_CREATED)
