"""API: GET /workout-plans/{workout_plan_id}/

Returns a workout plan with its routines (days) and exercises. Public
information.
"""

from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workout_plans.features.get_workout_plan_details_feature.services import (
    get_workout_plan_details,
)

from .get_workout_plan_details_serializers import (
    WorkoutPlanDetailsOutputSerializer,
)


class GetWorkoutPlanDetailsView(APIView):
    def get(self, request: Request, workout_plan_id: int) -> Response:
        workout_plan = get_workout_plan_details(workout_plan_id)
        if workout_plan is None:
            raise NotFound()
        return Response(WorkoutPlanDetailsOutputSerializer(workout_plan).data)
