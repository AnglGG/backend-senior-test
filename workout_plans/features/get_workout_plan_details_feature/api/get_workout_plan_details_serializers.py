"""Serializers for the get-workout-plan-details endpoint."""

from rest_framework import serializers

from workout_plans.models import Routine, RoutineExercise, WorkoutPlan


class _RoutineExerciseOutputSerializer(serializers.ModelSerializer):
    exercise_template_id = serializers.IntegerField()
    exercise_name = serializers.CharField(source="exercise_template.name")

    class Meta:
        model = RoutineExercise
        fields = (
            "id",
            "exercise_template_id",
            "exercise_name",
            "position",
            "target_sets",
            "target_reps_min",
            "target_reps_max",
            "target_weight_kg",
            "notes",
        )


class _RoutineOutputSerializer(serializers.ModelSerializer):
    exercises = _RoutineExerciseOutputSerializer(many=True)

    class Meta:
        model = Routine
        fields = (
            "id",
            "day_index",
            "name",
            "target_muscle_groups",
            "exercises",
        )


class WorkoutPlanDetailsOutputSerializer(serializers.ModelSerializer):
    routines = _RoutineOutputSerializer(many=True)

    class Meta:
        model = WorkoutPlan
        fields = (
            "id",
            "user_id",
            "name",
            "description",
            "goal",
            "frequency_per_week",
            "routines",
        )
