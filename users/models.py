"""Models for the `users` app.

Owns identity (`User`) and fitness-related profile data (`UserProfile`).
Profile is split out because identity and profile fields evolve at different
rates and are read in different contexts.
"""

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

from exercise_catalog.models import Equipment


class User(AbstractUser):
    """Application user.

    Extends Django's `AbstractUser` so it remains pluggable as `AUTH_USER_MODEL`
    even though authentication itself is out of scope for this codebase
    (see `README.md`). The `X-Test-User-Id` header resolves a `User` row
    without going through any login flow.
    """

    display_name = models.CharField(max_length=80, blank=True)
    avatar_url = models.URLField(blank=True)
    bio = models.CharField(max_length=280, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.display_name or self.username


class ExperienceLevel(models.TextChoices):
    BEGINNER = "BEGINNER", "Beginner"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ADVANCED = "ADVANCED", "Advanced"


class TrainingGoal(models.TextChoices):
    STRENGTH = "STRENGTH", "Strength"
    HYPERTROPHY = "HYPERTROPHY", "Hypertrophy"
    ENDURANCE = "ENDURANCE", "Endurance"
    WEIGHT_LOSS = "WEIGHT_LOSS", "Weight loss"
    GENERAL_FITNESS = "GENERAL_FITNESS", "General fitness"


class UserProfile(models.Model):
    """Fitness-domain data attached to a `User`.

    Kept as a separate row because profile fields churn independently of
    identity and are not needed on most authentication paths. The
    `experience_level` / `primary_goal` / `training_frequency_per_week` /
    `available_equipment` quartet is what any "what should I train next"
    recommender reads to seed its decisions.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    date_of_birth = models.DateField(null=True, blank=True)

    experience_level = models.CharField(
        max_length=16,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.BEGINNER,
    )
    primary_goal = models.CharField(
        max_length=24,
        choices=TrainingGoal.choices,
        default=TrainingGoal.GENERAL_FITNESS,
    )
    training_frequency_per_week = models.PositiveSmallIntegerField(default=3)
    available_equipment = ArrayField(
        base_field=models.CharField(max_length=16, choices=Equipment.choices),
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self) -> str:
        return f"Profile<{self.user_id}>"
