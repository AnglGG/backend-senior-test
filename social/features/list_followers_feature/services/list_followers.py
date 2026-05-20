"""Service: list users that follow a given user, most recent follow first."""

from django.db.models import QuerySet

from social.models import Following


def list_followers(*, user_id: int) -> QuerySet[Following]:
    return Following.objects.filter(
        followed_id=user_id
    ).select_related("follower").order_by("-created_at")
