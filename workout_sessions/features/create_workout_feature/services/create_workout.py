"""Service: create a workout session with its nested exercises and sets.

Persists the entire payload in a single transaction. Sets are inserted with
`bulk_create` to keep the round-trip count proportional to the number of
exercises, not the number of sets.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.db import transaction

from exercise_catalog.models import ExerciseTemplate
from users.models import User
from workout_sessions.models import (
    WorkoutSession,
    WorkoutSessionExercise,
    WorkoutSessionSet,
)


@dataclass(frozen=True)
class SetInput:
    position: int
    weight_kg: Decimal
    reps: int
    rpe: Decimal | None
    completed_at: datetime


@dataclass(frozen=True)
class ExerciseInput:
    exercise_template_id: int
    position: int
    notes: str
    sets: list[SetInput]


@dataclass(frozen=True)
class CreateWorkoutInput:
    name: str
    notes: str
    started_at: datetime
    finished_at: datetime | None
    exercises: list[ExerciseInput]


@transaction.atomic
def create_workout(*, user: User, payload: CreateWorkoutInput) -> WorkoutSession:
    workout_session = WorkoutSession.objects.create(
        user=user,
        name=payload.name,
        notes=payload.notes,
        started_at=payload.started_at,
        finished_at=payload.finished_at,
    )

    template_ids = {ex.exercise_template_id for ex in payload.exercises}
    templates_by_id = ExerciseTemplate.objects.in_bulk(template_ids)

    sets_to_create: list[WorkoutSessionSet] = []
    for exercise_input in payload.exercises:
        exercise = WorkoutSessionExercise.objects.create(
            workout_session=workout_session,
            exercise_template=templates_by_id[exercise_input.exercise_template_id],
            position=exercise_input.position,
            notes=exercise_input.notes,
        )
        for set_input in exercise_input.sets:
            sets_to_create.append(
                WorkoutSessionSet(
                    exercise=exercise,
                    position=set_input.position,
                    weight_kg=set_input.weight_kg,
                    reps=set_input.reps,
                    rpe=set_input.rpe,
                    completed_at=set_input.completed_at,
                )
            )

    WorkoutSessionSet.objects.bulk_create(sets_to_create)
    return workout_session
