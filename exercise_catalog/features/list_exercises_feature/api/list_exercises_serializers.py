"""Serializers for the list-exercises endpoint."""

from rest_framework import serializers

from exercise_catalog.models import ExerciseTemplate


class ListExercisesQuerySerializer(serializers.Serializer):
    muscle_group = serializers.CharField(required=False, allow_blank=True)
    equipment = serializers.CharField(required=False, allow_blank=True)
    search = serializers.CharField(required=False, allow_blank=True)


class ExerciseTemplateOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseTemplate
        fields = (
            "id",
            "name",
            "primary_muscle_group",
            "equipment",
            "instructions",
        )
