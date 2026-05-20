"""Service: start following a user.

Idempotent — calling twice with the same pair is a no-op and returns the
existing `Following` row. Self-follows are rejected before hitting the DB so
the caller gets a clean error instead of an `IntegrityError`.
"""

from django.db import transaction

from social.models import Following
from users.models import User


class SelfFollowNotAllowed(Exception):
    pass


@transaction.atomic
def follow_user(*, follower: User, target_user_id: int) -> Following:
    if follower.id == target_user_id:
        raise SelfFollowNotAllowed()

    following, _ = Following.objects.get_or_create(
        follower=follower,
        followed_id=target_user_id,
    )
    return following
