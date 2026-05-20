"""Serializers for the list-followers endpoint."""

from rest_framework import serializers


class FollowerOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="follower.id")
    display_name = serializers.CharField(source="follower.display_name")
    avatar_url = serializers.CharField(source="follower.avatar_url")
