"""Serializers for the create-workout endpoint.

The input serializer validates the HTTP payload and then converts it into a
`CreateWorkoutInput` dataclass that the service operates on.
"""

from rest_framework import serializers

from workout_sessions.features.create_workout_feature.services import (
    CreateWorkoutInput,
    ExerciseInput,
    SetInput,
)


class _SetInputSerializer(serializers.Serializer):
    position = serializers.IntegerField(min_value=1)
    weight_kg = serializers.DecimalField(max_digits=6, decimal_places=2)
    reps = serializers.IntegerField(min_value=1)
    rpe = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        required=False,
        allow_null=True,
    )
    completed_at = serializers.DateTimeField()


class _ExerciseInputSerializer(serializers.Serializer):
    exercise_template_id = serializers.IntegerField(min_value=1)
    position = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(allow_blank=True, max_length=240, default="")
    sets = _SetInputSerializer(many=True)


class CreateWorkoutInputSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True, max_length=120, default="")
    notes = serializers.CharField(allow_blank=True, default="")
    started_at = serializers.DateTimeField()
    finished_at = serializers.DateTimeField(required=False, allow_null=True)
    exercises = _ExerciseInputSerializer(many=True)

    def to_domain_input(self) -> CreateWorkoutInput:
        data = self.validated_data
        return CreateWorkoutInput(
            name=data["name"],
            notes=data["notes"],
            started_at=data["started_at"],
            finished_at=data.get("finished_at"),
            exercises=[
                ExerciseInput(
                    exercise_template_id=ex["exercise_template_id"],
                    position=ex["position"],
                    notes=ex["notes"],
                    sets=[
                        SetInput(
                            position=s["position"],
                            weight_kg=s["weight_kg"],
                            reps=s["reps"],
                            rpe=s.get("rpe"),
                            completed_at=s["completed_at"],
                        )
                        for s in ex["sets"]
                    ],
                )
                for ex in data["exercises"]
            ],
        )


class CreateWorkoutOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
