"""Service: update mutable fields of a workout session.

Only the owner can update; the API surface raises permission errors. The
service itself trusts the caller has already checked ownership.
"""

from __future__ import annotations

from dataclasses import dataclass

from workout_sessions.models import WorkoutSession


@dataclass(frozen=True)
class UpdateWorkoutInput:
    name: str | None = None
    notes: str | None = None


def update_workout(
    *,
    workout_session: WorkoutSession,
    payload: UpdateWorkoutInput,
) -> WorkoutSession:
    if payload.name is not None:
        workout_session.name = payload.name
    if payload.notes is not None:
        workout_session.notes = payload.notes
    workout_session.save()
    return workout_session
