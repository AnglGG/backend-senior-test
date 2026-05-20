"""Serializers for the list-workout-comments endpoint."""

from rest_framework import serializers

from social.models import WorkoutComment


class WorkoutCommentOutputSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    author_name = serializers.CharField(source="user.display_name")
    author_username = serializers.CharField(source="user.username")

    class Meta:
        model = WorkoutComment
        fields = (
            "id",
            "user_id",
            "author_name",
            "author_username",
            "body",
            "created_at",
        )
