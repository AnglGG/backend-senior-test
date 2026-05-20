"""Domain signals for the `users` app.

`UserProfile` is cached on the home-screen read path (see
`users.core.services.profile_cache`). The `post_save` handler below is the
contract that keeps that cache consistent: whenever a profile row is saved,
the cached entry for that user is dropped and the next read recomputes.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from users.core.services.profile_cache import invalidate_profile_summary
from users.models import UserProfile


@receiver(post_save, sender=UserProfile)
def drop_profile_summary_cache_on_save(
    sender,
    instance: UserProfile,
    **kwargs,
) -> None:
    invalidate_profile_summary(user_id=instance.user_id)
