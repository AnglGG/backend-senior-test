"""Service for the preferences endpoint."""

from rest_framework.exceptions import ValidationError

from exercise_catalog.models import ExerciseTemplate
from users.models import UserProfile


VALID_LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED"]
VALID_GOALS = [
    "STRENGTH",
    "HYPERTROPHY",
    "ENDURANCE",
    "WEIGHT_LOSS",
    "GENERAL_FITNESS",
]


def process_preferences_update(user, data):
    profile = UserProfile.objects.get(user=user)

    update_data = {}

    if "experience_level" in data:
        lvl = data["experience_level"]
        if lvl not in VALID_LEVELS:
            raise ValidationError("invalid experience_level")
        update_data["experience_level"] = lvl

    if "primary_goal" in data:
        g = data["primary_goal"]
        if g not in VALID_GOALS:
            raise ValidationError("invalid primary_goal")
        update_data["primary_goal"] = g

    if "training_frequency_per_week" in data:
        f = data["training_frequency_per_week"]
        if f < 1 or f > 7:
            raise ValidationError("training_frequency_per_week must be 1-7")
        update_data["training_frequency_per_week"] = f

    if "available_equipment" in data:
        eq = data["available_equipment"]
        valid_eq = list(
            ExerciseTemplate.objects.values_list("equipment", flat=True).distinct()
        )
        for item in eq:
            if item not in valid_eq:
                raise ValidationError("unknown equipment: " + item)
        update_data["available_equipment"] = eq

    UserProfile.objects.filter(user=user).update(**update_data)

    profile = UserProfile.objects.get(user=user)
    if profile.available_equipment:
        n = ExerciseTemplate.objects.filter(
            equipment__in=profile.available_equipment
        ).count()
    else:
        n = 0

    result = {
        "experience_level": profile.experience_level,
        "primary_goal": profile.primary_goal,
        "training_frequency_per_week": profile.training_frequency_per_week,
        "available_equipment": profile.available_equipment,
        "trainable_exercise_count": n,
    }
    return result
