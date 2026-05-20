"""Serializers for the create-workout-plan endpoint."""

from rest_framework import serializers

from exercise_catalog.models import MuscleGroup
from users.models import TrainingGoal
from workout_plans.features.create_workout_plan_feature.services import (
    CreateWorkoutPlanInput,
    RoutineExerciseInput,
    RoutineInput,
)


class _RoutineExerciseInputSerializer(serializers.Serializer):
    exercise_template_id = serializers.IntegerField(min_value=1)
    position = serializers.IntegerField(min_value=1)
    target_sets = serializers.IntegerField(min_value=1)
    target_reps_min = serializers.IntegerField(min_value=1)
    target_reps_max = serializers.IntegerField(min_value=1)
    target_weight_kg = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    notes = serializers.CharField(allow_blank=True, max_length=240, default="")


class _RoutineInputSerializer(serializers.Serializer):
    day_index = serializers.IntegerField(min_value=0)
    name = serializers.CharField(max_length=80)
    target_muscle_groups = serializers.ListField(
        child=serializers.ChoiceField(choices=MuscleGroup.choices),
        required=False,
        default=list,
    )
    exercises = _RoutineExerciseInputSerializer(many=True)


class CreateWorkoutPlanInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    description = serializers.CharField(allow_blank=True, default="")
    goal = serializers.ChoiceField(
        choices=TrainingGoal.choices,
        default=TrainingGoal.GENERAL_FITNESS,
    )
    frequency_per_week = serializers.IntegerField(min_value=1, max_value=7, default=3)
    routines = _RoutineInputSerializer(many=True)

    def to_domain_input(self) -> CreateWorkoutPlanInput:
        data = self.validated_data
        return CreateWorkoutPlanInput(
            name=data["name"],
            description=data["description"],
            goal=data["goal"],
            frequency_per_week=data["frequency_per_week"],
            routines=[
                RoutineInput(
                    day_index=routine["day_index"],
                    name=routine["name"],
                    target_muscle_groups=routine["target_muscle_groups"],
                    exercises=[
                        RoutineExerciseInput(
                            exercise_template_id=ex["exercise_template_id"],
                            position=ex["position"],
                            target_sets=ex["target_sets"],
                            target_reps_min=ex["target_reps_min"],
                            target_reps_max=ex["target_reps_max"],
                            target_weight_kg=ex.get("target_weight_kg"),
                            notes=ex["notes"],
                        )
                        for ex in routine["exercises"]
                    ],
                )
                for routine in data["routines"]
            ],
        )


class CreateWorkoutPlanOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
