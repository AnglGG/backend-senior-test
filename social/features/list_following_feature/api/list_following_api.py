"""API: GET /users/{user_id}/following/

Paginated list of users that `user_id` follows, most recent follow first.
"""

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from social.features.list_following_feature.services import list_following
from users.models import User

from .list_following_serializers import FollowingOutputSerializer


class _Pagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ListFollowingView(APIView):
    def get(self, request: Request, user_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        get_object_or_404(User, pk=user_id)

        queryset = list_following(user_id=user_id)
        paginator = _Pagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = FollowingOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
