"""API: DELETE /users/{target_user_id}/follow/

Idempotent. Returns 204 even when the caller was not following the user.
"""

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from social.features.unfollow_user_feature.services import unfollow_user


class UnfollowUserView(APIView):
    def delete(self, request: Request, target_user_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        unfollow_user(follower=request.user, target_user_id=target_user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
