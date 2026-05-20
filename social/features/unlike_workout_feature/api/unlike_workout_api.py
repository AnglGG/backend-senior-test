"""API: DELETE /workouts/{workout_id}/like/

Idempotent. Returns 204 even when the caller had not liked the workout.
"""

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from social.features.unlike_workout_feature.services import unlike_workout


class UnlikeWorkoutView(APIView):
    def delete(self, request: Request, workout_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        unlike_workout(user=request.user, workout_session_id=workout_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
