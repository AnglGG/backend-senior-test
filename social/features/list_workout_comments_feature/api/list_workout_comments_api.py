"""API: GET /workouts/{workout_id}/comments/

Paginated list of comments on a completed training session, oldest first.
"""

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from social.features.list_workout_comments_feature.services import (
    list_workout_comments,
)
from workout_sessions.core.services import can_view_workout
from workout_sessions.models import WorkoutSession

from .list_workout_comments_serializers import WorkoutCommentOutputSerializer


class _Pagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ListWorkoutCommentsView(APIView):
    def get(self, request: Request, workout_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        workout_session = get_object_or_404(WorkoutSession, pk=workout_id)
        if not can_view_workout(viewer=request.user, workout_session=workout_session):
            raise NotFound()

        queryset = list_workout_comments(workout_session_id=workout_id)
        paginator = _Pagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = WorkoutCommentOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
