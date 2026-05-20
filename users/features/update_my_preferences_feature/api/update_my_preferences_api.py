"""API: PATCH /users/me/preferences/"""

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.features.update_my_preferences_feature.services.update_my_preferences import (
    process_preferences_update,
)

from .update_my_preferences_serializers import UpdatePreferencesInputSerializer


class UpdateMyPreferencesView(APIView):
    @extend_schema(
        request=UpdatePreferencesInputSerializer,
        responses={
            200: inline_serializer(
                name="UpdateMyPreferencesResponse",
                fields={
                    "experience_level": serializers.CharField(),
                    "primary_goal": serializers.CharField(),
                    "training_frequency_per_week": serializers.IntegerField(),
                    "available_equipment": serializers.ListField(
                        child=serializers.CharField()
                    ),
                    "trainable_exercise_count": serializers.IntegerField(),
                },
            ),
        },
    )
    def patch(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        s = UpdatePreferencesInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        result = process_preferences_update(request.user, s.validated_data)
        return Response(result)
