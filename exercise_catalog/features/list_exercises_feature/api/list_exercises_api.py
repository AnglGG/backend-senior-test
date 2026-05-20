"""API: GET /exercises/

Paginated list of exercise templates, optionally filtered by muscle group,
equipment, or a substring search on the exercise name. This is a read-mostly
catalog endpoint.
"""

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from exercise_catalog.features.list_exercises_feature.services import list_exercises

from .list_exercises_serializers import (
    ExerciseTemplateOutputSerializer,
    ListExercisesQuerySerializer,
)


class ListExercisesPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class ListExercisesView(APIView):
    def get(self, request: Request) -> Response:
        query = ListExercisesQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        params = query.validated_data

        queryset = list_exercises(
            muscle_group=params.get("muscle_group") or None,
            equipment=params.get("equipment") or None,
            search=params.get("search") or None,
        )

        paginator = ListExercisesPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ExerciseTemplateOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
