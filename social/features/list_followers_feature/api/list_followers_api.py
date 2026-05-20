"""API: GET /users/{user_id}/followers/

Paginated list of users who follow `user_id`, most recent follow first.
"""

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from social.features.list_followers_feature.services import list_followers
from users.models import User

from .list_followers_serializers import FollowerOutputSerializer


class _Pagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ListFollowersView(APIView):
    def get(self, request: Request, user_id: int) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        get_object_or_404(User, pk=user_id)

        queryset = list_followers(user_id=user_id)
        paginator = _Pagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = FollowerOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
