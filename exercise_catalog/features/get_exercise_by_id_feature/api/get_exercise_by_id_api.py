"""API: GET /exercises/{exercise_id}/

Returns one exercise template with its aliases. 404 when the template does
not exist.
"""

from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from exercise_catalog.features.get_exercise_by_id_feature.services import (
    get_exercise_by_id,
)

from .get_exercise_by_id_serializers import ExerciseTemplateDetailsSerializer


class GetExerciseByIdView(APIView):
    def get(self, request: Request, exercise_id: int) -> Response:
        template = get_exercise_by_id(exercise_id)
        if template is None:
            raise NotFound()
        return Response(ExerciseTemplateDetailsSerializer(template).data)
