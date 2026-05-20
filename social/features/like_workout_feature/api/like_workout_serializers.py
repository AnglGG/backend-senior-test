"""Serializers for the like-workout endpoint."""

from rest_framework import serializers


class _LikerOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    display_name = serializers.CharField()
    avatar_url = serializers.CharField()


class LikeWorkoutOutputSerializer(serializers.Serializer):
    user = _LikerOutputSerializer()
    created_at = serializers.DateTimeField()
