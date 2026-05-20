"""API: POST /users/{target_user_id}/follow/

Idempotent — calling more than once does not produce duplicate rows.
Self-follows are rejected with 400.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from social.features.follow_user_feature.services import (
    SelfFollowNotAllowed,
    follow_user,
)
from users.models import User

from .follow_user_serializers import FollowUserOutputSerializer


class FollowUserView(APIView):
    def post(self, request: Request, target_user_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        target_user = get_object_or_404(User, pk=target_user_id)

        try:
            following = follow_user(
                follower=request.user, target_user_id=target_user_id
            )
        except SelfFollowNotAllowed:
            raise ValidationError({"detail": "Users cannot follow themselves."})

        return Response(
            FollowUserOutputSerializer({
                "followed": {
                    "id": target_user.id,
                    "display_name": target_user.display_name,
                    "avatar_url": target_user.avatar_url,
                },
                "created_at": following.created_at,
            }).data,
            status=status.HTTP_201_CREATED,
        )
