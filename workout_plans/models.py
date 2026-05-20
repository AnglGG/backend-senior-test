"""Models for the `workout_plans` app.

This app owns **the plans users intend to train** — structured templates
that prescribe what *should* be done, not what *has* been done. A
`WorkoutPlan` is a multi-day training plan (e.g. an upper/lower split,
push/pull/legs); each `Routine` inside it represents one of the plan's
days. `UserActiveWorkoutPlan` tracks which plan a user is currently
following and where they are in the rotation.

Relationship to the other training-domain apps:

- `exercise_catalog`   →  the catalog   ("what exercises exist")
- `workout_plans`      →  the plan      ("what I intend to train")
- `workout_sessions`   →  the log       ("what I actually did")

The naming mirrors the execution side: a `Routine` (intent for one day) is
the natural counterpart of a `WorkoutSession` (execution of one day);
`RoutineExercise` prescribes what `WorkoutSessionExercise` later records.

A `WorkoutPlan` is composed of `Routine` rows (Push Day, Pull Day…); each
routine lists the `RoutineExercise` rows that prescribe sets, rep ranges,
and an optional target weight. `RoutineExercise.exercise_template` points at
`exercise_catalog.ExerciseTemplate` for the canonical exercise definition.

Nothing in this app records actual performance — that lives in
`workout_sessions`.
"""

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from exercise_catalog.models import ExerciseTemplate, MuscleGroup
from users.models import TrainingGoal


class WorkoutPlan(models.Model):
    """A multi-day training plan owned by a user (e.g. an upper/lower split)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_plans",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    goal = models.CharField(
        max_length=24,
        choices=TrainingGoal.choices,
        default=TrainingGoal.GENERAL_FITNESS,
    )
    frequency_per_week = models.PositiveSmallIntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workout_plans"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.name


class Routine(models.Model):
    """One day inside a `WorkoutPlan` (e.g. "Push Day", "Day 1: Upper").

    `day_index` defines the rotation order inside the plan; it is unique per
    plan so reordering remains deterministic. `target_muscle_groups` is a
    denormalized hint used by the "what should I train today" path so a
    consumer can reason about coverage without joining through exercises.
    """

    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name="routines",
    )
    day_index = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=80)
    target_muscle_groups = ArrayField(
        base_field=models.CharField(max_length=16, choices=MuscleGroup.choices),
        default=list,
        blank=True,
    )

    class Meta:
        db_table = "routines"
        ordering = ["workout_plan_id", "day_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_plan", "day_index"],
                name="routine_unique_day_index_per_plan",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} (plan={self.workout_plan_id})"


class RoutineExercise(models.Model):
    """An `ExerciseTemplate` prescribed within a `Routine` (one day).

    Targets are stored as ranges (`target_reps_min`..`target_reps_max`) because
    most plans prescribe a band rather than a fixed rep count.
    `target_weight_kg` is optional — many plans leave the load to the lifter's
    discretion.
    """

    routine = models.ForeignKey(
        Routine,
        on_delete=models.CASCADE,
        related_name="exercises",
    )
    exercise_template = models.ForeignKey(
        ExerciseTemplate,
        on_delete=models.PROTECT,
        related_name="+",
    )
    position = models.PositiveSmallIntegerField()
    target_sets = models.PositiveSmallIntegerField()
    target_reps_min = models.PositiveSmallIntegerField()
    target_reps_max = models.PositiveSmallIntegerField()
    target_weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    notes = models.CharField(max_length=240, blank=True)

    class Meta:
        db_table = "routine_exercises"
        ordering = ["routine_id", "position"]
        constraints = [
            models.UniqueConstraint(
                fields=["routine", "position"],
                name="routine_exercise_unique_position",
            ),
        ]

    def __str__(self) -> str:
        return f"RoutineExercise<{self.pk}>"


class UserActiveWorkoutPlan(models.Model):
    """The plan a user is currently following.

    At most one row per user — the one-to-one relation enforces that.
    `current_day_index` is the next `Routine.day_index` the user is expected
    to train; it advances on session completion and wraps around at the end
    of the rotation.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="active_workout_plan",
    )
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name="+",
    )
    current_day_index = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_active_workout_plans"

    def __str__(self) -> str:
        return f"ActiveWorkoutPlan<user={self.user_id} plan={self.workout_plan_id}>"
