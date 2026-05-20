"""Serializers for the get-my-profile endpoint."""

from rest_framework import serializers


class _ActiveWorkoutPlanSummarySerializer(serializers.Serializer):
    workout_plan_id = serializers.IntegerField()
    workout_plan_name = serializers.CharField()
    current_day_index = serializers.IntegerField()
    started_at = serializers.DateTimeField()


class _UserProfileSerializer(serializers.Serializer):
    height_cm = serializers.IntegerField(allow_null=True)
    weight_kg = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True,
    )
    date_of_birth = serializers.DateField(allow_null=True)
    experience_level = serializers.CharField()
    primary_goal = serializers.CharField()
    training_frequency_per_week = serializers.IntegerField()
    available_equipment = serializers.ListField(child=serializers.CharField())


class MyProfileOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    display_name = serializers.CharField()
    avatar_url = serializers.CharField(allow_blank=True)
    bio = serializers.CharField(allow_blank=True)
    profile = _UserProfileSerializer(allow_null=True)
    active_workout_plan = _ActiveWorkoutPlanSummarySerializer(allow_null=True)
