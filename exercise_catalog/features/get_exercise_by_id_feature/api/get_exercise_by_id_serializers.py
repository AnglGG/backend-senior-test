"""Serializers for the get-exercise-by-id endpoint."""

from rest_framework import serializers

from exercise_catalog.models import ExerciseTemplate, ExerciseTemplateAlias


class _ExerciseTemplateAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseTemplateAlias
        fields = ("name", "locale")


class ExerciseTemplateDetailsSerializer(serializers.ModelSerializer):
    aliases = _ExerciseTemplateAliasSerializer(many=True)

    class Meta:
        model = ExerciseTemplate
        fields = (
            "id",
            "name",
            "primary_muscle_group",
            "secondary_muscle_groups",
            "equipment",
            "difficulty_level",
            "instructions",
            "usage_count",
            "aliases",
        )
