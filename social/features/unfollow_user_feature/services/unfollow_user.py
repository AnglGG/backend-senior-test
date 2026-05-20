"""Service: stop following a user.

Idempotent — deleting a non-existent `Following` row is a no-op.
"""

from social.models import Following
from users.models import User


def unfollow_user(*, follower: User, target_user_id: int) -> None:
    Following.objects.filter(
        follower=follower,
        followed_id=target_user_id,
    ).delete()
