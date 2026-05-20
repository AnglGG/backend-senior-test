"""API: GET /users/{user_id}/workout-plans/

Paginated list of a user's workout plans, newest first. Public information —
the viewer does not need to share any relationship with the target user.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workout_plans.features.list_user_workout_plans_feature.services import (
    list_user_workout_plans,
)

from .list_user_workout_plans_serializers import WorkoutPlanSummarySerializer


class _Pagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ListUserWorkoutPlansView(APIView):
    def get(self, request: Request, user_id: int) -> Response:
        queryset = list_user_workout_plans(user_id=user_id)
        paginator = _Pagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = WorkoutPlanSummarySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
