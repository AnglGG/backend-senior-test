"""API: POST /workout-plans/

Creates a workout plan owned by the requesting user along with its nested
routines (days) and exercises.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workout_plans.features.create_workout_plan_feature.services import (
    create_workout_plan,
)

from .create_workout_plan_serializers import (
    CreateWorkoutPlanInputSerializer,
    CreateWorkoutPlanOutputSerializer,
)


class CreateWorkoutPlanView(APIView):
    @extend_schema(
        request=CreateWorkoutPlanInputSerializer,
        responses={201: CreateWorkoutPlanOutputSerializer},
    )
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        serializer = CreateWorkoutPlanInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workout_plan = create_workout_plan(
            user=request.user,
            payload=serializer.to_domain_input(),
        )

        return Response(
            CreateWorkoutPlanOutputSerializer({"id": workout_plan.id}).data,
            status=status.HTTP_201_CREATED,
        )
