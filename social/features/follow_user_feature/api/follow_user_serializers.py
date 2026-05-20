"""Serializers for the follow-user endpoint."""

from rest_framework import serializers


class _FollowedUserOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    display_name = serializers.CharField()
    avatar_url = serializers.CharField()


class FollowUserOutputSerializer(serializers.Serializer):
    followed = _FollowedUserOutputSerializer()
    created_at = serializers.DateTimeField()
