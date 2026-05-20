"""Models for the `social` app.

Connects users to each other (`Following`) and to other users' workout
sessions (`WorkoutLike`, `WorkoutComment`). All three are high-traffic
tables on the read path of any social feed.
"""

from django.conf import settings
from django.db import models

from workout_sessions.models import WorkoutSession


class Following(models.Model):
    """One user following another.

    The `(follower, followed)` pair is unique. Self-follows are forbidden by a
    check constraint so callers don't need to guard against it.
    """

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "followings"
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"],
                name="following_unique_pair",
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("followed")),
                name="following_no_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["followed", "follower"]),
        ]

    def __str__(self) -> str:
        return f"Following<{self.follower_id}->{self.followed_id}>"


class WorkoutLike(models.Model):
    """A user liking a completed training session."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_likes",
    )
    workout_session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workout_likes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "workout_session"],
                name="workout_like_unique_per_user",
            ),
        ]
        indexes = [
            models.Index(fields=["workout_session", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"WorkoutLike<user={self.user_id} session={self.workout_session_id}>"


class WorkoutComment(models.Model):
    """A comment a user wrote on a completed training session."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_comments",
    )
    workout_session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workout_comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["workout_session", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"WorkoutComment<{self.pk}>"
