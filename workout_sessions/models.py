"""Models for the `workout_sessions` app.

This app owns **what users have actually trained** — the immutable log of
completed sessions. A `WorkoutSession` is one training session a user
completed at a specific moment, with real weights, real reps, and real
timestamps.

Relationship to the other training-domain apps:

- `exercise_catalog`   →  the catalog   ("what exercises exist")
- `workout_plans`      →  the plan      ("what I intend to train")
- `workout_sessions`   →  the log       ("what I actually did")

A `WorkoutSession` belongs to a user and contains an ordered list of
`WorkoutSessionExercise` rows, each of which contains an ordered list of
`WorkoutSessionSet` rows. `PersonalRecord` and `MuscleGroupRecovery` are
precomputed read projections over `WorkoutSessionSet`, refreshed when a
session closes; they exist because computing them on demand from raw sets
is unfeasible once a user accumulates years of training data.

Nothing in this app prescribes what to do next — that lives in `workout_plans`.
"""

from django.conf import settings
from django.db import models

from exercise_catalog.models import ExerciseTemplate, MuscleGroup


class WorkoutSession(models.Model):
    """A workout session a user completed.

    The whole app is a *private social network*: a workout is visible to its
    owner and to the accounts following the owner. There is no per-workout
    visibility setting — that complexity is out of scope.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_sessions",
    )
    name = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workout_sessions"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "-started_at"]),
        ]

    def __str__(self) -> str:
        return self.name or f"WorkoutSession<{self.pk}>"


class WorkoutSessionExercise(models.Model):
    """An `ExerciseTemplate` performed inside a specific `WorkoutSession`.

    `position` preserves the order the user trained the exercises in;
    `(workout_session, position)` is unique so swaps and inserts stay
    deterministic.
    """

    workout_session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name="exercises",
    )
    exercise_template = models.ForeignKey(
        ExerciseTemplate,
        on_delete=models.PROTECT,
        related_name="+",
    )
    position = models.PositiveSmallIntegerField()
    notes = models.CharField(max_length=240, blank=True)

    class Meta:
        db_table = "workout_session_exercises"
        ordering = ["workout_session_id", "position"]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_session", "position"],
                name="workout_session_exercise_unique_position",
            ),
        ]

    def __str__(self) -> str:
        return f"WorkoutSessionExercise<{self.pk}>"


class WorkoutSessionSet(models.Model):
    """A single set within a `WorkoutSessionExercise`.

    This is the highest-volume row in the schema (multiple per exercise,
    multiple exercises per session, many sessions per user). Any read that
    aggregates across sets needs to be designed with that fan-out in mind.
    """

    exercise = models.ForeignKey(
        WorkoutSessionExercise,
        on_delete=models.CASCADE,
        related_name="sets",
    )
    position = models.PositiveSmallIntegerField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    reps = models.PositiveSmallIntegerField()
    rpe = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
    )
    completed_at = models.DateTimeField()

    class Meta:
        db_table = "workout_session_sets"
        ordering = ["exercise_id", "position"]
        constraints = [
            models.UniqueConstraint(
                fields=["exercise", "position"],
                name="workout_session_set_unique_position_per_exercise",
            ),
        ]
        indexes = [
            models.Index(fields=["-completed_at"]),
        ]

    def __str__(self) -> str:
        return f"WorkoutSessionSet<{self.pk}>"


class PersonalRecord(models.Model):
    """Per-(user, exercise) top performance, precomputed.

    Maintained as a denormalized row rather than computed on demand: the
    upstream `WorkoutSessionSet` table is large enough that a "best set for
    this user on this exercise" query is not viable on the read path.
    Refresh logic lives outside the model itself.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="personal_records",
    )
    exercise_template = models.ForeignKey(
        ExerciseTemplate,
        on_delete=models.CASCADE,
        related_name="+",
    )
    best_weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    best_reps_at_weight = models.PositiveSmallIntegerField()
    source_set = models.ForeignKey(
        WorkoutSessionSet,
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    achieved_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "personal_records"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "exercise_template"],
                name="personal_record_unique_per_user_exercise",
            ),
        ]

    def __str__(self) -> str:
        return f"PersonalRecord<user={self.user_id} exercise={self.exercise_template_id}>"


class MuscleGroupRecovery(models.Model):
    """Per-(user, muscle_group) last-trained timestamp, precomputed.

    Powers the "what should I train today" decision: rather than scanning all
    of a user's `WorkoutSessionSet` rows to figure out which muscle group is
    most rested, a single row per (user, muscle_group) keeps the answer one
    lookup away. Refresh logic lives outside the model and runs when a
    session closes.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="muscle_group_recoveries",
    )
    muscle_group = models.CharField(
        max_length=16,
        choices=MuscleGroup.choices,
    )
    last_trained_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "muscle_group_recoveries"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "muscle_group"],
                name="muscle_group_recovery_unique_per_user",
            ),
        ]

    def __str__(self) -> str:
        return f"Recovery<user={self.user_id} group={self.muscle_group}>"
