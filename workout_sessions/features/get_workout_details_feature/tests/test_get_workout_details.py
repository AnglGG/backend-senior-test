"""Tests for the get-workout-details endpoint.

This is the local template for how tests are written in this codebase.
The conventions on display here are worth copying when you write your own:

- DRF's `APITestCase` is the base.
- URLs are resolved via `reverse(...)` with the app namespace so a rename
  of the path does not break the test.
- The caller is set with the `X-Test-User-Id` header (see `users.authentication`).
  Django's test client expects it as the `HTTP_X_TEST_USER_ID` META key.
- Test names describe the contract under test (CG8.1 in `CODING_GUIDELINES.md`),
  not the HTTP verb or status code.
"""

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from workout_sessions.models import WorkoutSession


class GetWorkoutDetailsTests(APITestCase):
    def setUp(self) -> None:
        self.owner = User.objects.create_user(
            username="owner",
            display_name="Owner",
        )
        self.non_follower = User.objects.create_user(
            username="non_follower",
            display_name="Non Follower",
        )
        self.workout = WorkoutSession.objects.create(
            user=self.owner,
            name="Leg day",
            started_at=timezone.now(),
        )

    def _details_url(self, workout_id: int) -> str:
        return reverse(
            "workout_sessions:details",
            kwargs={"workout_id": workout_id},
        )

    def _as(self, user: User) -> dict[str, str]:
        return {"HTTP_X_TEST_USER_ID": str(user.id)}

    def test_owner_sees_their_own_workout(self) -> None:
        response = self.client.get(
            self._details_url(self.workout.id),
            **self._as(self.owner),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.workout.id)
        self.assertEqual(response.data["owner"]["id"], self.owner.id)

    def test_workout_returns_404_for_non_follower(self) -> None:
        response = self.client.get(
            self._details_url(self.workout.id),
            **self._as(self.non_follower),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
