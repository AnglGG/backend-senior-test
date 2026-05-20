# Symmetry's Backend Architecture

A Django project split into **bounded contexts (apps)**, where every endpoint lives in its own **vertical slice** under that app's `features/` folder. The full layer-by-layer rules are in [`CODING_GUIDELINES.md`](CODING_GUIDELINES.md); this file is the map.

## Bounded contexts

```
                ┌──────────────────┐
                │ exercise_catalog │
                │                  │
                │  "What exercises │
                │       exist"     │
                └────────┬─────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
   ┌──────────────────┐    ┌────────────────────┐
   │  workout_plans   │    │  workout_sessions  │
   │  "What I intend  │    │  "What I actually  │
   │    to train"     │    │       did"         │
   └──────────────────┘    └────────────────────┘

   ┌──────────────────┐    ┌────────────────────┐
   │      users       │    │       social       │
   │   Identity &     │    │    Follows,        │
   │   preferences    │    │    likes, comments │
   └──────────────────┘    └────────────────────┘
```

The training-domain mental model:
- **`exercise_catalog`** is static, shared, read-mostly. "Bench Press" exists once; every user references it.
- **`workout_plans`** is intentional and prescriptive. What the user *intends* to do.
- **`workout_sessions`** is factual and historical. What the user *actually did*, with timestamps and concrete loads.

If you are unsure where a piece of code belongs, ask:
- Is it about the *definition* of an exercise? → `exercise_catalog`.
- Is it about *what the user plans to do*? → `workout_plans`.
- Is it about *what the user has done*? → `workout_sessions`.

## Plan ↔ session symmetry

The naming on both sides mirrors deliberately:

| Concept                  | Plan side                       | Execution side          |
| ------------------------ | ------------------------------- | ----------------------- |
| The whole multi-day plan | `WorkoutPlan`                   | *(no equivalent — each session is independent)* |
| One day                  | `Routine`                       | `WorkoutSession`        |
| One exercise in a day    | `RoutineExercise`               | `WorkoutSessionExercise`|
| One set in an exercise   | *(prescribed by `target_*`)*    | `WorkoutSessionSet`     |
| The active selection     | `UserActiveWorkoutPlan`         | —                       |

## Folder structure per app

```
<app>/
├── models.py                                  ORM definitions.
├── core/
│   ├── apis/
│   │   ├── urls.py                            Registers every feature's APIView.
│   │   └── domain_to_domain/                  Public callables OTHER apps consume.
│   └── services/                              Logic shared between features of this app.
└── features/
    └── <action>_<noun>_feature/
        ├── __init__.py                        Re-exports the public service callable.
        ├── api/
        │   ├── <feature>_api.py               The APIView. HTTP concerns only.
        │   └── <feature>_serializers.py
        ├── services/
        │   └── <action>.py                    The business logic.
        └── tests/
```

Reading a whole feature should mean opening **one folder**. If you find yourself jumping across five apps to follow a request, the feature is wrong.

### `core/services/` vs `core/apis/domain_to_domain/`
Both folders exist for shared logic, but they answer different questions:
- **`core/services/<x>.py`** — *intra-domain*. Use it when two or more features inside **this same app** need the same piece of logic.
- **`core/apis/domain_to_domain/<x>.py`** — *cross-domain*. Use it when **another app** needs to call into this one. The callable here is the only sanctioned cross-app entry point: consumers import from `<app>.core.apis.domain_to_domain` instead of reaching into `<app>.models` directly.

Folders are created only when there is a real callable that lives in them — don't pre-create empty ones.

## URL routing
`config/urls.py` includes `<app>/core/apis/urls.py` for every app. URLs reflect the *resource*, not the bounded context — `POST /workouts/{id}/like/` is served by a view in `social/features/like_workout_feature/` but registered from `workout_sessions/core/apis/urls.py`, because the resource is the workout.

## Authentication
There is none. Real auth is out of scope. The `X-Test-User-Id` header resolves the requesting user via `users.authentication.XTestUserAuthentication` (a DRF `BaseAuthentication` backend). Endpoints that need a user check `request.user.is_authenticated`.
