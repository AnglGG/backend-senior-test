"""Serializers for the add-workout-comment endpoint."""

from rest_framework import serializers

from social.models import WorkoutComment


class AddWorkoutCommentInputSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=500)


class _AuthorOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    display_name = serializers.CharField()
    avatar_url = serializers.CharField()


class AddWorkoutCommentOutputSerializer(serializers.ModelSerializer):
    author = _AuthorOutputSerializer(source="user")

    class Meta:
        model = WorkoutComment
        fields = ("id", "author", "body", "created_at")
