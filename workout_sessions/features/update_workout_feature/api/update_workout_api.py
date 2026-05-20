"""API: PATCH /workouts/{workout_id}/update/

Only the owner can update a session. Non-owners receive 404 — the same
response that hides the existence of private sessions — to keep ownership
information from leaking.
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workout_sessions.features.update_workout_feature.services import update_workout
from workout_sessions.models import WorkoutSession

from .update_workout_serializers import (
    UpdateWorkoutInputSerializer,
    UpdateWorkoutOutputSerializer,
)


class UpdateWorkoutView(APIView):
    @extend_schema(
        request=UpdateWorkoutInputSerializer,
        responses={200: UpdateWorkoutOutputSerializer},
    )
    def patch(self, request: Request, workout_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        workout_session = get_object_or_404(WorkoutSession, pk=workout_id)
        if workout_session.user_id != request.user.id:
            raise NotFound()

        serializer = UpdateWorkoutInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = update_workout(
            workout_session=workout_session,
            payload=serializer.to_domain_input(),
        )

        return Response(UpdateWorkoutOutputSerializer({
            "id": updated.id,
            "name": updated.name,
            "notes": updated.notes,
        }).data)
