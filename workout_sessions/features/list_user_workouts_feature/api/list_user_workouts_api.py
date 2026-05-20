"""API: GET /users/{user_id}/workouts/

Returns a user's workout history, newest first. Offset/limit pagination —
callers should pass `offset` and `limit` query parameters.
"""

from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from workout_sessions.features.list_user_workouts_feature.services import (
    list_user_workouts,
)

from .list_user_workouts_serializers import WorkoutSummarySerializer


DEFAULT_LIMIT = 20
MAX_LIMIT = 100


class ListUserWorkoutsView(APIView):
    def get(self, request: Request, user_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        offset = _parse_int(request.query_params.get("offset"), default=0, minimum=0)
        limit = _parse_int(
            request.query_params.get("limit"),
            default=DEFAULT_LIMIT,
            minimum=1,
            maximum=MAX_LIMIT,
        )

        workouts = list_user_workouts(
            target_user_id=user_id,
            offset=offset,
            limit=limit,
        )

        serializer = WorkoutSummarySerializer(workouts, many=True)
        return Response({
            "results": serializer.data,
            "offset": offset,
            "limit": limit,
        })


def _parse_int(
    raw: str | None,
    *,
    default: int,
    minimum: int,
    maximum: int | None = None,
) -> int:
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    if value < minimum:
        return minimum
    if maximum is not None and value > maximum:
        return maximum
    return value
