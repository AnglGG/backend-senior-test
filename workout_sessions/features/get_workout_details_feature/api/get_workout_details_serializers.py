"""Serializers for the workout-details endpoint."""

from rest_framework import serializers

from workout_sessions.models import (
    WorkoutSession,
    WorkoutSessionExercise,
    WorkoutSessionSet,
)


class _WorkoutSessionSetOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSessionSet
        fields = ("id", "position", "weight_kg", "reps", "rpe", "completed_at")


class _WorkoutSessionExerciseOutputSerializer(serializers.ModelSerializer):
    exercise_template_id = serializers.IntegerField()
    exercise_name = serializers.CharField(source="exercise_template.name")
    sets = _WorkoutSessionSetOutputSerializer(many=True)

    class Meta:
        model = WorkoutSessionExercise
        fields = (
            "id",
            "exercise_template_id",
            "exercise_name",
            "position",
            "notes",
            "sets",
        )


class _OwnerOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    display_name = serializers.CharField()
    avatar_url = serializers.CharField()


class WorkoutDetailsOutputSerializer(serializers.ModelSerializer):
    owner = _OwnerOutputSerializer(source="user")
    exercises = _WorkoutSessionExerciseOutputSerializer(many=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WorkoutSession
        fields = (
            "id",
            "owner",
            "name",
            "notes",
            "started_at",
            "finished_at",
            "exercises",
            "like_count",
            "comment_count",
        )
