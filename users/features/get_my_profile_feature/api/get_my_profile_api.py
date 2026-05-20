"""API: GET /users/me/

Returns the current user with their profile and active routine summary.
"""

from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.features.get_my_profile_feature.services import get_my_profile

from .get_my_profile_serializers import MyProfileOutputSerializer


class GetMyProfileView(APIView):
    def get(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        user = get_my_profile(request.user)
        return Response(MyProfileOutputSerializer(user).data)
