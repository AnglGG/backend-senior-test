"""Serializers for the update-workout endpoint."""

from rest_framework import serializers

from workout_sessions.features.update_workout_feature.services import UpdateWorkoutInput


class UpdateWorkoutInputSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=120, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def to_domain_input(self) -> UpdateWorkoutInput:
        data = self.validated_data
        return UpdateWorkoutInput(
            name=data.get("name"),
            notes=data.get("notes"),
        )


class UpdateWorkoutOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    notes = serializers.CharField()
