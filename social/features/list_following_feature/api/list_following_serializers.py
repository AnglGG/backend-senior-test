"""Serializers for the list-following endpoint."""

from rest_framework import serializers


class FollowingOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="followed.id")
    display_name = serializers.CharField(source="followed.display_name")
    avatar_url = serializers.CharField(source="followed.avatar_url")
