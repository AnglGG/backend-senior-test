"""Service: create a workout plan with its nested routines (days) and exercises."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from exercise_catalog.models import ExerciseTemplate
from users.models import User
from workout_plans.models import Routine, RoutineExercise, WorkoutPlan


@dataclass(frozen=True)
class RoutineExerciseInput:
    exercise_template_id: int
    position: int
    target_sets: int
    target_reps_min: int
    target_reps_max: int
    target_weight_kg: Decimal | None
    notes: str


@dataclass(frozen=True)
class RoutineInput:
    day_index: int
    name: str
    target_muscle_groups: list[str]
    exercises: list[RoutineExerciseInput]


@dataclass(frozen=True)
class CreateWorkoutPlanInput:
    name: str
    description: str
    goal: str
    frequency_per_week: int
    routines: list[RoutineInput]


@transaction.atomic
def create_workout_plan(
    *, user: User, payload: CreateWorkoutPlanInput
) -> WorkoutPlan:
    workout_plan = WorkoutPlan.objects.create(
        user=user,
        name=payload.name,
        description=payload.description,
        goal=payload.goal,
        frequency_per_week=payload.frequency_per_week,
    )

    template_ids = {
        exercise.exercise_template_id
        for routine in payload.routines
        for exercise in routine.exercises
    }
    templates_by_id = ExerciseTemplate.objects.in_bulk(template_ids)

    exercises_to_create: list[RoutineExercise] = []
    for routine_input in payload.routines:
        routine = Routine.objects.create(
            workout_plan=workout_plan,
            day_index=routine_input.day_index,
            name=routine_input.name,
            target_muscle_groups=routine_input.target_muscle_groups,
        )
        for exercise_input in routine_input.exercises:
            exercises_to_create.append(
                RoutineExercise(
                    routine=routine,
                    exercise_template=templates_by_id[exercise_input.exercise_template_id],
                    position=exercise_input.position,
                    target_sets=exercise_input.target_sets,
                    target_reps_min=exercise_input.target_reps_min,
                    target_reps_max=exercise_input.target_reps_max,
                    target_weight_kg=exercise_input.target_weight_kg,
                    notes=exercise_input.notes,
                )
            )

    RoutineExercise.objects.bulk_create(exercises_to_create)
    return workout_plan
