"""Service: list users that a given user follows, most recent follow first."""

from django.db.models import QuerySet

from social.models import Following


def list_following(*, user_id: int) -> QuerySet[Following]:
    return Following.objects.filter(
        follower_id=user_id
    ).select_related("followed").order_by("-created_at")
