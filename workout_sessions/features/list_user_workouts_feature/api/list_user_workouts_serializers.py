"""Serializers for the list-user-workouts endpoint."""

from rest_framework import serializers

from workout_sessions.models import WorkoutSession


class WorkoutSummarySerializer(serializers.ModelSerializer):
    """Compact summary of a completed session used by the timeline view."""

    exercise_count = serializers.SerializerMethodField()
    set_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutSession
        fields = (
            "id",
            "name",
            "started_at",
            "finished_at",
            "exercise_count",
            "set_count",
            "like_count",
            "comment_count",
        )

    def get_exercise_count(self, obj: WorkoutSession) -> int:
        return obj.exercises.count()

    def get_set_count(self, obj: WorkoutSession) -> int:
        total = 0
        for exercise in obj.exercises.all():
            total += exercise.sets.count()
        return total

    def get_like_count(self, obj: WorkoutSession) -> int:
        return obj.likes.count()

    def get_comment_count(self, obj: WorkoutSession) -> int:
        return obj.comments.count()
