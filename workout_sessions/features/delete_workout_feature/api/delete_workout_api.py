"""API: DELETE /workouts/{workout_id}/delete/

Only the owner can delete. Non-owners receive 404 to avoid leaking ownership.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workout_sessions.features.delete_workout_feature.services import delete_workout
from workout_sessions.models import WorkoutSession


class DeleteWorkoutView(APIView):
    def delete(self, request: Request, workout_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        workout_session = get_object_or_404(WorkoutSession, pk=workout_id)
        if workout_session.user_id != request.user.id:
            raise NotFound()

        delete_workout(workout_session=workout_session)
        return Response(status=status.HTTP_204_NO_CONTENT)
