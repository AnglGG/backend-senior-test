"""API: GET /workouts/{workout_id}/

Returns the session if it exists and the requesting user is allowed to see it.
A session the viewer cannot read is reported as 404 to avoid leaking its
existence; the same response covers a genuinely missing id.
"""

from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workout_sessions.core.services import can_view_workout
from workout_sessions.features.get_workout_details_feature.services import (
    get_workout_details,
)

from .get_workout_details_serializers import WorkoutDetailsOutputSerializer


class GetWorkoutDetailsView(APIView):
    def get(self, request: Request, workout_id: int) -> Response:
        workout_session = get_workout_details(workout_id)
        if workout_session is None:
            raise NotFound()

        if not can_view_workout(viewer=request.user, workout_session=workout_session):
            raise NotFound()

        serializer = WorkoutDetailsOutputSerializer(workout_session)
        return Response(serializer.data)
