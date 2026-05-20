"""Models for the `exercises` app.

This app owns the **read-mostly catalog of canonical exercises**.
An `ExerciseTemplate` is the abstract "Bench Press" entry: the static
definition of an exercise as it exists in the world, independent of any
particular user or training session.

Relationship to the other training-domain apps:

- `exercise_catalog`   →  the catalog   ("what exercises exist")
- `workout_plans`      →  the plan      ("what I intend to train")
- `workout_sessions`   →  the log       ("what I actually did")

Both `workout_plans.RoutineExercise` and
`workout_sessions.WorkoutSessionExercise` hold a foreign key to
`ExerciseTemplate` here. Templates are seeded once and rarely change;
isolating them keeps both downstream apps free of reference data.

`ExerciseTemplateAlias` carries the alternative names (synonyms, translations)
the search path uses to resolve user input to a canonical template.
"""

from django.contrib.postgres.fields import ArrayField
from django.db import models


class MuscleGroup(models.TextChoices):
    CHEST = "CHEST", "Chest"
    BACK = "BACK", "Back"
    SHOULDERS = "SHOULDERS", "Shoulders"
    BICEPS = "BICEPS", "Biceps"
    TRICEPS = "TRICEPS", "Triceps"
    LEGS = "LEGS", "Legs"
    GLUTES = "GLUTES", "Glutes"
    CORE = "CORE", "Core"
    FULL_BODY = "FULL_BODY", "Full body"


class Equipment(models.TextChoices):
    BARBELL = "BARBELL", "Barbell"
    DUMBBELL = "DUMBBELL", "Dumbbell"
    MACHINE = "MACHINE", "Machine"
    CABLE = "CABLE", "Cable"
    BODYWEIGHT = "BODYWEIGHT", "Bodyweight"
    KETTLEBELL = "KETTLEBELL", "Kettlebell"
    BAND = "BAND", "Resistance band"


class DifficultyLevel(models.TextChoices):
    BEGINNER = "BEGINNER", "Beginner"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ADVANCED = "ADVANCED", "Advanced"


class ExerciseTemplate(models.Model):
    """Canonical exercise that users reference from their workout logs.

    `usage_count` is denormalized: it represents how many times the template
    has been logged across all users. The catalog ranks by it on the read path
    so popular exercises surface first without paying for an aggregate query.
    """

    name = models.CharField(max_length=120, unique=True)
    primary_muscle_group = models.CharField(
        max_length=16,
        choices=MuscleGroup.choices,
    )
    secondary_muscle_groups = ArrayField(
        base_field=models.CharField(max_length=16, choices=MuscleGroup.choices),
        default=list,
        blank=True,
    )
    equipment = models.CharField(
        max_length=16,
        choices=Equipment.choices,
    )
    difficulty_level = models.CharField(
        max_length=16,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.INTERMEDIATE,
    )
    instructions = models.TextField(blank=True)
    usage_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercise_templates"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["primary_muscle_group"]),
            models.Index(fields=["-usage_count"]),
        ]

    def __str__(self) -> str:
        return self.name


class ExerciseTemplateAlias(models.Model):
    """An alternative or translated name for an `ExerciseTemplate`.

    `(name, locale)` is unique so the catalog can index by locale and a single
    template can carry many aliases per language (synonyms, slang).
    """

    template = models.ForeignKey(
        ExerciseTemplate,
        on_delete=models.CASCADE,
        related_name="aliases",
    )
    name = models.CharField(max_length=120)
    locale = models.CharField(max_length=8, default="en")

    class Meta:
        db_table = "exercise_template_aliases"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "locale"],
                name="exercise_alias_unique_name_per_locale",
            ),
        ]
        indexes = [
            models.Index(fields=["locale", "name"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} [{self.locale}]"
