"""Test authentication backend for Symmetry Lite.

This codebase intentionally has no real authentication layer (see README).
`XTestUserAuthentication` resolves the requesting user from the
`X-Test-User-Id` header so DRF views can rely on `request.user` exactly as
they would behind a real auth backend.

A missing or malformed header is treated as "anonymous": the authenticator
returns `None`, which lets DRF fall through to `AnonymousUser` and lets views
decide for themselves whether the endpoint is public or requires a user.
"""

from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

User = get_user_model()


class XTestUserAuthentication(BaseAuthentication):
    HEADER = "X-Test-User-Id"

    def authenticate(self, request):
        raw_user_id = request.headers.get(self.HEADER)
        if not raw_user_id:
            return None

        try:
            user_id = int(raw_user_id)
        except ValueError:
            return None

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        return (user, None)
