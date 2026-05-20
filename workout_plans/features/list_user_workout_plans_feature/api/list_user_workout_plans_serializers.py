"""Serializers for the list-user-workout-plans endpoint."""

from rest_framework import serializers

from workout_plans.models import WorkoutPlan


class WorkoutPlanSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutPlan
        fields = (
            "id",
            "name",
            "goal",
            "frequency_per_week",
            "created_at",
        )
