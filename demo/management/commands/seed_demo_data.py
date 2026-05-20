"""`python manage.py seed_demo_data`

Populates the database with a realistic demo dataset so the API has something
to return out of the box. Idempotent: if any `ExerciseTemplate` already
exists the command exits without writing.

Determinism: every random source is seeded with the same constant, so the
dataset is reproducible across runs.
"""

from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from exercise_catalog.models import (
    DifficultyLevel,
    Equipment,
    ExerciseTemplate,
    ExerciseTemplateAlias,
    MuscleGroup,
)
from social.models import Following, WorkoutComment, WorkoutLike
from users.models import (
    ExperienceLevel,
    TrainingGoal,
    User,
    UserProfile,
)
from workout_plans.models import (
    Routine,
    RoutineExercise,
    UserActiveWorkoutPlan,
    WorkoutPlan,
)
from workout_sessions.models import (
    MuscleGroupRecovery,
    PersonalRecord,
    WorkoutSession,
    WorkoutSessionExercise,
    WorkoutSessionSet,
)


SEED = 42
USER_COUNT = 120
PLANS_PER_USER_RANGE = (1, 2)
ROUTINES_PER_PLAN_RANGE = (3, 5)
EXERCISES_PER_ROUTINE_RANGE = (6, 8)
ACTIVE_PLAN_RATIO = 0.80
SESSIONS_PER_USER_RANGE = (30, 70)
SESSION_LOOKBACK_DAYS = 90
EXERCISES_PER_SESSION_RANGE = (4, 8)
SETS_PER_EXERCISE_RANGE = (3, 5)
FOLLOWING_DENSITY = 0.06
LIKE_RATIO = 0.18
COMMENT_RATIO = 0.05
SET_BULK_BATCH_SIZE = 2000


EXERCISE_CATALOG: list[dict] = [
    # CHEST
    {"name": "Barbell Bench Press", "primary": MuscleGroup.CHEST, "secondary": [MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Press de banca", "es"), ("Bench Press", "en")]},
    {"name": "Incline Bench Press", "primary": MuscleGroup.CHEST, "secondary": [MuscleGroup.SHOULDERS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Press inclinado", "es"), ("Incline Press", "en")]},
    {"name": "Dumbbell Bench Press", "primary": MuscleGroup.CHEST, "secondary": [MuscleGroup.TRICEPS], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Press con mancuernas", "es")]},
    {"name": "Push-Up", "primary": MuscleGroup.CHEST, "secondary": [MuscleGroup.TRICEPS, MuscleGroup.CORE], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Flexión", "es"), ("Press-Up", "en")]},
    {"name": "Cable Crossover", "primary": MuscleGroup.CHEST, "secondary": [], "equipment": Equipment.CABLE, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Cruce de poleas", "es")]},
    {"name": "Chest Fly", "primary": MuscleGroup.CHEST, "secondary": [], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Aperturas", "es")]},
    {"name": "Decline Bench Press", "primary": MuscleGroup.CHEST, "secondary": [MuscleGroup.TRICEPS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Press declinado", "es")]},
    {"name": "Pec Deck Machine", "primary": MuscleGroup.CHEST, "secondary": [], "equipment": Equipment.MACHINE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Contractor de pecho", "es")]},
    # BACK
    {"name": "Pull-Up", "primary": MuscleGroup.BACK, "secondary": [MuscleGroup.BICEPS], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Dominadas", "es"), ("Chin-Up", "en")]},
    {"name": "Lat Pulldown", "primary": MuscleGroup.BACK, "secondary": [MuscleGroup.BICEPS], "equipment": Equipment.CABLE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Jalón al pecho", "es")]},
    {"name": "Barbell Row", "primary": MuscleGroup.BACK, "secondary": [MuscleGroup.BICEPS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Remo con barra", "es"), ("Bent-Over Row", "en")]},
    {"name": "Dumbbell Row", "primary": MuscleGroup.BACK, "secondary": [MuscleGroup.BICEPS], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Remo con mancuerna", "es")]},
    {"name": "T-Bar Row", "primary": MuscleGroup.BACK, "secondary": [], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Remo en T", "es")]},
    {"name": "Seated Cable Row", "primary": MuscleGroup.BACK, "secondary": [MuscleGroup.BICEPS], "equipment": Equipment.CABLE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Remo en polea baja", "es")]},
    {"name": "Face Pull", "primary": MuscleGroup.BACK, "secondary": [MuscleGroup.SHOULDERS], "equipment": Equipment.CABLE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Face pull", "es")]},
    {"name": "Barbell Shrug", "primary": MuscleGroup.BACK, "secondary": [], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Encogimientos", "es")]},
    # SHOULDERS
    {"name": "Overhead Press", "primary": MuscleGroup.SHOULDERS, "secondary": [MuscleGroup.TRICEPS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Press militar", "es"), ("Military Press", "en")]},
    {"name": "Dumbbell Shoulder Press", "primary": MuscleGroup.SHOULDERS, "secondary": [MuscleGroup.TRICEPS], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Press de hombro con mancuernas", "es")]},
    {"name": "Lateral Raise", "primary": MuscleGroup.SHOULDERS, "secondary": [], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Elevaciones laterales", "es"), ("Side Raise", "en")]},
    {"name": "Front Raise", "primary": MuscleGroup.SHOULDERS, "secondary": [], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Elevaciones frontales", "es")]},
    {"name": "Rear Delt Fly", "primary": MuscleGroup.SHOULDERS, "secondary": [MuscleGroup.BACK], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Pájaros", "es")]},
    {"name": "Arnold Press", "primary": MuscleGroup.SHOULDERS, "secondary": [MuscleGroup.TRICEPS], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Press Arnold", "es")]},
    {"name": "Upright Row", "primary": MuscleGroup.SHOULDERS, "secondary": [MuscleGroup.BACK], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Remo al mentón", "es")]},
    # BICEPS
    {"name": "Barbell Curl", "primary": MuscleGroup.BICEPS, "secondary": [], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Curl con barra", "es")]},
    {"name": "Dumbbell Curl", "primary": MuscleGroup.BICEPS, "secondary": [], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Curl con mancuernas", "es")]},
    {"name": "Hammer Curl", "primary": MuscleGroup.BICEPS, "secondary": [], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Curl martillo", "es")]},
    {"name": "Preacher Curl", "primary": MuscleGroup.BICEPS, "secondary": [], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Curl en banco scott", "es")]},
    {"name": "Cable Curl", "primary": MuscleGroup.BICEPS, "secondary": [], "equipment": Equipment.CABLE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Curl en polea", "es")]},
    {"name": "Concentration Curl", "primary": MuscleGroup.BICEPS, "secondary": [], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Curl concentrado", "es")]},
    # TRICEPS
    {"name": "Tricep Dip", "primary": MuscleGroup.TRICEPS, "secondary": [MuscleGroup.CHEST], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Fondos en paralelas", "es")]},
    {"name": "Skull Crusher", "primary": MuscleGroup.TRICEPS, "secondary": [], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Press francés", "es"), ("Lying Tricep Extension", "en")]},
    {"name": "Tricep Pushdown", "primary": MuscleGroup.TRICEPS, "secondary": [], "equipment": Equipment.CABLE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Extensiones de triceps", "es")]},
    {"name": "Overhead Tricep Extension", "primary": MuscleGroup.TRICEPS, "secondary": [], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Extensión por encima de la cabeza", "es")]},
    {"name": "Diamond Push-Up", "primary": MuscleGroup.TRICEPS, "secondary": [MuscleGroup.CHEST], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Flexiones diamante", "es")]},
    # LEGS
    {"name": "Barbell Squat", "primary": MuscleGroup.LEGS, "secondary": [MuscleGroup.GLUTES, MuscleGroup.CORE], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Sentadilla con barra", "es"), ("Back Squat", "en")]},
    {"name": "Leg Press", "primary": MuscleGroup.LEGS, "secondary": [MuscleGroup.GLUTES], "equipment": Equipment.MACHINE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Prensa", "es")]},
    {"name": "Walking Lunge", "primary": MuscleGroup.LEGS, "secondary": [MuscleGroup.GLUTES], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Zancadas", "es")]},
    {"name": "Deadlift", "primary": MuscleGroup.LEGS, "secondary": [MuscleGroup.BACK, MuscleGroup.GLUTES], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.ADVANCED, "aliases": [("Peso muerto", "es")]},
    {"name": "Romanian Deadlift", "primary": MuscleGroup.LEGS, "secondary": [MuscleGroup.GLUTES, MuscleGroup.BACK], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Peso muerto rumano", "es"), ("RDL", "en")]},
    {"name": "Leg Extension", "primary": MuscleGroup.LEGS, "secondary": [], "equipment": Equipment.MACHINE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Extensiones de cuadriceps", "es")]},
    {"name": "Leg Curl", "primary": MuscleGroup.LEGS, "secondary": [], "equipment": Equipment.MACHINE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Curl femoral", "es")]},
    {"name": "Calf Raise", "primary": MuscleGroup.LEGS, "secondary": [], "equipment": Equipment.MACHINE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Elevaciones de gemelos", "es")]},
    {"name": "Bulgarian Split Squat", "primary": MuscleGroup.LEGS, "secondary": [MuscleGroup.GLUTES], "equipment": Equipment.DUMBBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Sentadilla búlgara", "es")]},
    # GLUTES
    {"name": "Hip Thrust", "primary": MuscleGroup.GLUTES, "secondary": [MuscleGroup.LEGS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Empuje de cadera", "es")]},
    {"name": "Glute Bridge", "primary": MuscleGroup.GLUTES, "secondary": [], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Puente de glúteos", "es")]},
    {"name": "Cable Kickback", "primary": MuscleGroup.GLUTES, "secondary": [], "equipment": Equipment.CABLE, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Patada en polea", "es")]},
    # CORE
    {"name": "Plank", "primary": MuscleGroup.CORE, "secondary": [], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Plancha", "es")]},
    {"name": "Crunch", "primary": MuscleGroup.CORE, "secondary": [], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Abdominal", "es"), ("Sit-Up", "en")]},
    {"name": "Russian Twist", "primary": MuscleGroup.CORE, "secondary": [], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.BEGINNER, "aliases": [("Giro ruso", "es")]},
    {"name": "Hanging Leg Raise", "primary": MuscleGroup.CORE, "secondary": [], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Elevación de piernas colgado", "es")]},
    {"name": "Ab Wheel Rollout", "primary": MuscleGroup.CORE, "secondary": [], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.ADVANCED, "aliases": [("Rueda abdominal", "es")]},
    # FULL BODY
    {"name": "Burpee", "primary": MuscleGroup.FULL_BODY, "secondary": [], "equipment": Equipment.BODYWEIGHT, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Burpee", "es")]},
    {"name": "Kettlebell Swing", "primary": MuscleGroup.FULL_BODY, "secondary": [MuscleGroup.GLUTES, MuscleGroup.BACK], "equipment": Equipment.KETTLEBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Swing con kettlebell", "es")]},
    {"name": "Clean and Jerk", "primary": MuscleGroup.FULL_BODY, "secondary": [MuscleGroup.LEGS, MuscleGroup.SHOULDERS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.ADVANCED, "aliases": [("Dos tiempos", "es")]},
    {"name": "Snatch", "primary": MuscleGroup.FULL_BODY, "secondary": [MuscleGroup.LEGS, MuscleGroup.SHOULDERS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.ADVANCED, "aliases": [("Arrancada", "es")]},
    {"name": "Thruster", "primary": MuscleGroup.FULL_BODY, "secondary": [MuscleGroup.LEGS, MuscleGroup.SHOULDERS], "equipment": Equipment.BARBELL, "difficulty": DifficultyLevel.INTERMEDIATE, "aliases": [("Thruster", "es")]},
]


ROUTINE_TEMPLATES = {
    "Push Day": [MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
    "Pull Day": [MuscleGroup.BACK, MuscleGroup.BICEPS],
    "Leg Day": [MuscleGroup.LEGS, MuscleGroup.GLUTES],
    "Upper Body": [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS, MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
    "Lower Body": [MuscleGroup.LEGS, MuscleGroup.GLUTES, MuscleGroup.CORE],
    "Full Body A": [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.LEGS],
    "Full Body B": [MuscleGroup.SHOULDERS, MuscleGroup.LEGS, MuscleGroup.CORE],
    "Arms Day": [MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
    "Core & Conditioning": [MuscleGroup.CORE, MuscleGroup.FULL_BODY],
}


GOAL_REP_RANGES = {
    TrainingGoal.STRENGTH: (3, 5),
    TrainingGoal.HYPERTROPHY: (8, 12),
    TrainingGoal.ENDURANCE: (15, 20),
    TrainingGoal.WEIGHT_LOSS: (12, 15),
    TrainingGoal.GENERAL_FITNESS: (8, 12),
}


EQUIPMENT_OPTIONS = [
    Equipment.BARBELL,
    Equipment.DUMBBELL,
    Equipment.MACHINE,
    Equipment.CABLE,
    Equipment.BODYWEIGHT,
    Equipment.KETTLEBELL,
    Equipment.BAND,
]


class Command(BaseCommand):
    help = "Populate the database with a realistic demo dataset (idempotent)."

    def handle(self, *args, **options):
        if ExerciseTemplate.objects.exists():
            self.stdout.write("Demo data already loaded, skipping.")
            return

        random.seed(SEED)
        faker = Faker(["en_US"])
        Faker.seed(SEED)

        with transaction.atomic():
            self.stdout.write("Seeding exercise catalog…")
            templates = self._seed_exercise_catalog()
            self.stdout.write(f"  {len(templates)} templates, {ExerciseTemplateAlias.objects.count()} aliases")

            self.stdout.write("Seeding users…")
            users = self._seed_users(faker)
            self.stdout.write(f"  {len(users)} users")

            self.stdout.write("Seeding workout plans…")
            plans, routines, _ = self._seed_workout_plans(users, templates)
            self.stdout.write(f"  {len(plans)} plans, {len(routines)} routines, {RoutineExercise.objects.count()} routine exercises")

            self.stdout.write("Seeding active workout plans…")
            active_count = self._seed_active_plans(users, plans)
            self.stdout.write(f"  {active_count} users have an active plan")

            self.stdout.write("Seeding workout sessions (this is the heavy bit)…")
            sessions, exercise_count, set_count = self._seed_workout_sessions(users, templates)
            self.stdout.write(f"  {len(sessions)} sessions, {exercise_count} exercises, {set_count} sets")

            self.stdout.write("Seeding following graph…")
            follow_count = self._seed_followings(users)
            self.stdout.write(f"  {follow_count} following edges")

            self.stdout.write("Seeding likes & comments…")
            like_count, comment_count = self._seed_social_engagement(users, sessions, faker)
            self.stdout.write(f"  {like_count} likes, {comment_count} comments")

            self.stdout.write("Seeding personal records…")
            pr_count = self._seed_personal_records()
            self.stdout.write(f"  {pr_count} personal records")

            self.stdout.write("Seeding muscle group recovery…")
            recovery_count = self._seed_muscle_group_recovery()
            self.stdout.write(f"  {recovery_count} recovery rows")

        self.stdout.write(self.style.SUCCESS("Demo data loaded."))

    # ------------------------------------------------------------------ catalog

    def _seed_exercise_catalog(self) -> list[ExerciseTemplate]:
        templates: list[ExerciseTemplate] = []
        aliases: list[ExerciseTemplateAlias] = []

        for entry in EXERCISE_CATALOG:
            template = ExerciseTemplate.objects.create(
                name=entry["name"],
                primary_muscle_group=entry["primary"],
                secondary_muscle_groups=entry["secondary"],
                equipment=entry["equipment"],
                difficulty_level=entry["difficulty"],
                usage_count=0,
            )
            templates.append(template)
            for alias_name, locale in entry["aliases"]:
                aliases.append(
                    ExerciseTemplateAlias(template=template, name=alias_name, locale=locale)
                )

        ExerciseTemplateAlias.objects.bulk_create(aliases)
        return templates

    # ------------------------------------------------------------------ users

    def _seed_users(self, faker: Faker) -> list[User]:
        users: list[User] = []
        profiles: list[UserProfile] = []

        for index in range(USER_COUNT):
            username = f"{faker.user_name()}_{index}"
            user = User.objects.create(
                username=username[:150],
                display_name=faker.name(),
                bio=faker.sentence(nb_words=8),
            )
            users.append(user)

            profiles.append(
                UserProfile(
                    user=user,
                    height_cm=random.randint(155, 195),
                    weight_kg=Decimal(random.randint(50, 110)),
                    experience_level=random.choice(list(ExperienceLevel)),
                    primary_goal=random.choice(list(TrainingGoal)),
                    training_frequency_per_week=random.randint(2, 6),
                    available_equipment=random.sample(EQUIPMENT_OPTIONS, k=random.randint(2, 5)),
                )
            )

        UserProfile.objects.bulk_create(profiles)
        return users

    # ------------------------------------------------------------------ plans

    def _seed_workout_plans(
        self,
        users: list[User],
        templates: list[ExerciseTemplate],
    ) -> tuple[list[WorkoutPlan], list[Routine], list[RoutineExercise]]:
        templates_by_muscle = self._group_templates_by_muscle(templates)

        plans: list[WorkoutPlan] = []
        routines: list[Routine] = []
        routine_exercises: list[RoutineExercise] = []

        for user in users:
            plan_count = random.randint(*PLANS_PER_USER_RANGE)
            for _ in range(plan_count):
                goal = random.choice(list(TrainingGoal))
                plan = WorkoutPlan.objects.create(
                    user=user,
                    name=self._make_plan_name(),
                    description="",
                    goal=goal,
                    frequency_per_week=random.randint(3, 6),
                )
                plans.append(plan)

                routine_count = random.randint(*ROUTINES_PER_PLAN_RANGE)
                routine_template_names = random.sample(
                    list(ROUTINE_TEMPLATES.keys()),
                    k=min(routine_count, len(ROUTINE_TEMPLATES)),
                )

                for day_index, routine_name in enumerate(routine_template_names):
                    target_muscles = ROUTINE_TEMPLATES[routine_name]
                    routine = Routine.objects.create(
                        workout_plan=plan,
                        day_index=day_index,
                        name=routine_name,
                        target_muscle_groups=target_muscles,
                    )
                    routines.append(routine)

                    candidate_templates = self._pick_templates_for_muscles(
                        templates_by_muscle, target_muscles
                    )
                    exercise_count = min(
                        random.randint(*EXERCISES_PER_ROUTINE_RANGE),
                        len(candidate_templates),
                    )
                    chosen = random.sample(candidate_templates, k=exercise_count)

                    rep_low, rep_high = GOAL_REP_RANGES[goal]
                    for position, template in enumerate(chosen, start=1):
                        target_weight = self._suggest_target_weight(template)
                        routine_exercises.append(
                            RoutineExercise(
                                routine=routine,
                                exercise_template=template,
                                position=position,
                                target_sets=random.randint(3, 4),
                                target_reps_min=rep_low,
                                target_reps_max=rep_high,
                                target_weight_kg=target_weight,
                                notes="",
                            )
                        )

        RoutineExercise.objects.bulk_create(routine_exercises, batch_size=SET_BULK_BATCH_SIZE)
        return plans, routines, routine_exercises

    @staticmethod
    def _make_plan_name() -> str:
        adjectives = ["Strength", "Hypertrophy", "Cutting", "Bulking", "Maintenance", "Push/Pull/Legs", "Upper/Lower"]
        return f"{random.choice(adjectives)} Plan {random.randint(1, 99)}"

    @staticmethod
    def _group_templates_by_muscle(
        templates: list[ExerciseTemplate],
    ) -> dict[str, list[ExerciseTemplate]]:
        grouped: dict[str, list[ExerciseTemplate]] = {}
        for template in templates:
            grouped.setdefault(template.primary_muscle_group, []).append(template)
        return grouped

    @staticmethod
    def _pick_templates_for_muscles(
        grouped: dict[str, list[ExerciseTemplate]],
        muscles: list[str],
    ) -> list[ExerciseTemplate]:
        pool: list[ExerciseTemplate] = []
        for muscle in muscles:
            pool.extend(grouped.get(muscle, []))
        return pool

    @staticmethod
    def _suggest_target_weight(template: ExerciseTemplate) -> Decimal | None:
        if template.equipment == Equipment.BODYWEIGHT:
            return None
        base_by_muscle = {
            MuscleGroup.LEGS: 80,
            MuscleGroup.BACK: 60,
            MuscleGroup.CHEST: 60,
            MuscleGroup.SHOULDERS: 30,
            MuscleGroup.GLUTES: 60,
            MuscleGroup.BICEPS: 15,
            MuscleGroup.TRICEPS: 20,
            MuscleGroup.CORE: 10,
            MuscleGroup.FULL_BODY: 40,
        }
        base = base_by_muscle.get(template.primary_muscle_group, 30)
        return Decimal(base + random.randint(-10, 30))

    # -------------------------------------------------------------- active plans

    def _seed_active_plans(
        self,
        users: list[User],
        plans: list[WorkoutPlan],
    ) -> int:
        plans_by_user: dict[int, list[WorkoutPlan]] = {}
        for plan in plans:
            plans_by_user.setdefault(plan.user_id, []).append(plan)

        active_rows: list[UserActiveWorkoutPlan] = []
        for user in users:
            user_plans = plans_by_user.get(user.id)
            if not user_plans:
                continue
            if random.random() > ACTIVE_PLAN_RATIO:
                continue
            active_rows.append(
                UserActiveWorkoutPlan(
                    user=user,
                    workout_plan=random.choice(user_plans),
                    current_day_index=random.randint(0, 2),
                )
            )

        UserActiveWorkoutPlan.objects.bulk_create(active_rows)
        return len(active_rows)

    # -------------------------------------------------------------- sessions

    def _seed_workout_sessions(
        self,
        users: list[User],
        templates: list[ExerciseTemplate],
    ) -> tuple[list[WorkoutSession], int, int]:
        templates_by_muscle = self._group_templates_by_muscle(templates)
        now = timezone.now()

        sessions: list[WorkoutSession] = []
        # Build sessions first to obtain ids.
        for user in users:
            session_count = random.randint(*SESSIONS_PER_USER_RANGE)
            for _ in range(session_count):
                days_ago = random.randint(0, SESSION_LOOKBACK_DAYS)
                started = now - timedelta(days=days_ago, hours=random.randint(0, 12))
                duration = timedelta(minutes=random.randint(40, 95))
                sessions.append(
                    WorkoutSession(
                        user=user,
                        name=random.choice(
                            ["Push", "Pull", "Legs", "Upper", "Lower", "Full", "Easy day", "PR attempt"]
                        ),
                        notes="",
                        started_at=started,
                        finished_at=started + duration,
                    )
                )

        WorkoutSession.objects.bulk_create(sessions, batch_size=SET_BULK_BATCH_SIZE)
        sessions = list(WorkoutSession.objects.order_by("id"))

        # Sort each user's sessions by date for progressive overload.
        sessions_by_user: dict[int, list[WorkoutSession]] = {}
        for session in sessions:
            sessions_by_user.setdefault(session.user_id, []).append(session)
        for session_list in sessions_by_user.values():
            session_list.sort(key=lambda s: s.started_at)

        # Build exercises and sets in two passes (exercises first to obtain ids).
        exercises_to_create: list[WorkoutSessionExercise] = []
        # Track muscle order per session so we can pick coherent exercises.
        for session in sessions:
            muscle_count = random.randint(2, 3)
            muscles = random.sample(
                [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS, MuscleGroup.LEGS,
                 MuscleGroup.BICEPS, MuscleGroup.TRICEPS, MuscleGroup.CORE, MuscleGroup.GLUTES],
                k=muscle_count,
            )
            candidate_templates = self._pick_templates_for_muscles(templates_by_muscle, muscles)
            exercise_count = min(
                random.randint(*EXERCISES_PER_SESSION_RANGE),
                len(candidate_templates),
            )
            picks = random.sample(candidate_templates, k=exercise_count)
            for position, template in enumerate(picks, start=1):
                exercises_to_create.append(
                    WorkoutSessionExercise(
                        workout_session=session,
                        exercise_template=template,
                        position=position,
                        notes="",
                    )
                )

        WorkoutSessionExercise.objects.bulk_create(
            exercises_to_create, batch_size=SET_BULK_BATCH_SIZE
        )
        exercises = list(WorkoutSessionExercise.objects.select_related("exercise_template").order_by("id"))

        # Sets: track running max per (user, exercise_template) for progressive overload.
        running_max: dict[tuple[int, int], Decimal] = {}
        sets_to_create: list[WorkoutSessionSet] = []

        for exercise in exercises:
            session = next(s for s in sessions_by_user[exercise.workout_session.user_id] if s.id == exercise.workout_session_id)
            user_id = exercise.workout_session.user_id
            template = exercise.exercise_template
            key = (user_id, template.id)
            base_weight = self._suggest_target_weight(template)
            current_max = running_max.get(key)
            if current_max is None:
                current_max = base_weight if base_weight is not None else Decimal("0")
            # Progressive overload: 1-2kg up each subsequent session for non-bodyweight.
            if template.equipment != Equipment.BODYWEIGHT:
                current_max += Decimal(random.choice([0, 1, 1, 2]))
            running_max[key] = current_max

            set_count = random.randint(*SETS_PER_EXERCISE_RANGE)
            rep_target = random.randint(6, 12)
            for set_position in range(1, set_count + 1):
                if template.equipment == Equipment.BODYWEIGHT:
                    weight = Decimal("0")
                else:
                    drop = Decimal(set_position - 1) * Decimal("2.5")
                    weight = max(current_max - drop, Decimal("10"))
                reps = max(1, rep_target - (set_position - 1))
                rpe = Decimal(min(10, 6 + set_position)).quantize(Decimal("0.1"))
                completed_at = session.started_at + timedelta(minutes=10 + set_position * 2)
                sets_to_create.append(
                    WorkoutSessionSet(
                        exercise=exercise,
                        position=set_position,
                        weight_kg=weight,
                        reps=reps,
                        rpe=rpe,
                        completed_at=completed_at,
                    )
                )

        WorkoutSessionSet.objects.bulk_create(sets_to_create, batch_size=SET_BULK_BATCH_SIZE)

        # Bump usage_count on templates.
        usage = {}
        for exercise in exercises:
            usage[exercise.exercise_template_id] = usage.get(exercise.exercise_template_id, 0) + 1
        for template_id, count in usage.items():
            ExerciseTemplate.objects.filter(pk=template_id).update(usage_count=count)

        return sessions, len(exercises_to_create), len(sets_to_create)

    # -------------------------------------------------------------- followings

    def _seed_followings(self, users: list[User]) -> int:
        edges: list[Following] = []
        seen: set[tuple[int, int]] = set()
        # Hub-and-spoke: a few "influencer" users get more followers than others.
        influencers = random.sample(users, k=min(10, len(users)))

        for follower in users:
            # Each user follows the influencers with higher probability.
            for influencer in influencers:
                if follower.id == influencer.id:
                    continue
                if random.random() < 0.4:
                    pair = (follower.id, influencer.id)
                    if pair not in seen:
                        seen.add(pair)
                        edges.append(Following(follower=follower, followed=influencer))

            # Random extra follows.
            extra_target_count = random.randint(0, int(len(users) * FOLLOWING_DENSITY))
            extra_targets = random.sample(users, k=min(extra_target_count, len(users)))
            for target in extra_targets:
                if follower.id == target.id:
                    continue
                pair = (follower.id, target.id)
                if pair not in seen:
                    seen.add(pair)
                    edges.append(Following(follower=follower, followed=target))

        Following.objects.bulk_create(edges)
        return len(edges)

    # -------------------------------------------------------------- engagement

    def _seed_social_engagement(
        self,
        users: list[User],
        sessions: list[WorkoutSession],
        faker: Faker,
    ) -> tuple[int, int]:
        # The app is a private social network: only followers ever see a
        # session. The seed simplifies that to "anyone can like" because demo
        # data does not need to be production-honest.
        now = timezone.now()

        likes: list[WorkoutLike] = []
        comments: list[WorkoutComment] = []

        for session in sessions:
            session_age_days = (now - session.started_at).days
            recency_weight = max(0.2, 1 - session_age_days / SESSION_LOOKBACK_DAYS)

            for user in users:
                if user.id == session.user_id:
                    continue
                if random.random() < LIKE_RATIO * recency_weight:
                    likes.append(WorkoutLike(user=user, workout_session=session))
                if random.random() < COMMENT_RATIO * recency_weight:
                    comments.append(
                        WorkoutComment(
                            user=user,
                            workout_session=session,
                            body=faker.sentence(nb_words=random.randint(4, 12))[:500],
                        )
                    )

        WorkoutLike.objects.bulk_create(likes, batch_size=SET_BULK_BATCH_SIZE)
        WorkoutComment.objects.bulk_create(comments, batch_size=SET_BULK_BATCH_SIZE)
        return len(likes), len(comments)

    # -------------------------------------------------------------- prs

    def _seed_personal_records(self) -> int:
        records: list[PersonalRecord] = []
        # Per (user, exercise_template) — pick the heaviest set.
        best_sets = (
            WorkoutSessionSet.objects
            .select_related("exercise__exercise_template", "exercise__workout_session__user")
            .order_by("-weight_kg")
        )
        seen: set[tuple[int, int]] = set()
        for s in best_sets.iterator(chunk_size=1000):
            user_id = s.exercise.workout_session.user_id
            template_id = s.exercise.exercise_template_id
            key = (user_id, template_id)
            if key in seen:
                continue
            seen.add(key)
            if s.weight_kg <= 0:
                continue
            records.append(
                PersonalRecord(
                    user_id=user_id,
                    exercise_template_id=template_id,
                    best_weight_kg=s.weight_kg,
                    best_reps_at_weight=s.reps,
                    source_set=s,
                    achieved_at=s.completed_at,
                )
            )
            if len(records) >= 1000:
                PersonalRecord.objects.bulk_create(records, batch_size=SET_BULK_BATCH_SIZE)
                records.clear()
        if records:
            PersonalRecord.objects.bulk_create(records, batch_size=SET_BULK_BATCH_SIZE)
        return PersonalRecord.objects.count()

    # -------------------------------------------------------------- recovery

    def _seed_muscle_group_recovery(self) -> int:
        # Per (user, muscle_group) — when did the user last train that group.
        rows: list[MuscleGroupRecovery] = []
        recent_sessions = (
            WorkoutSessionExercise.objects
            .select_related("workout_session", "exercise_template")
            .order_by("-workout_session__started_at")
        )
        seen: set[tuple[int, str]] = set()
        for row in recent_sessions.iterator(chunk_size=1000):
            user_id = row.workout_session.user_id
            muscle = row.exercise_template.primary_muscle_group
            key = (user_id, muscle)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                MuscleGroupRecovery(
                    user_id=user_id,
                    muscle_group=muscle,
                    last_trained_at=row.workout_session.started_at,
                )
            )
            if len(rows) >= 2000:
                MuscleGroupRecovery.objects.bulk_create(rows, batch_size=SET_BULK_BATCH_SIZE)
                rows.clear()
        if rows:
            MuscleGroupRecovery.objects.bulk_create(rows, batch_size=SET_BULK_BATCH_SIZE)
        return MuscleGroupRecovery.objects.count()
