"""OpenAPI customisations for the Symmetry Lite schema.

Two customisations on top of drf-spectacular defaults:

1. `DomainTaggedAutoSchema` re-tags each operation by the Django app that owns
   the view (not by URL prefix), so the docs are organised by bounded context.
   Summaries and descriptions are pulled from the view module's docstring,
   which every `*_api.py` file already carries.

2. `XTestUserAuthScheme` teaches the schema generator about the
   `X-Test-User-Id` header so Swagger UI shows an "Authorize" button and
   "Try it out" requests include the header automatically.
"""

from inspect import getmodule

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.openapi import AutoSchema


class DomainTaggedAutoSchema(AutoSchema):
    def get_tags(self) -> list[str]:
        module = self.view.__class__.__module__
        # `social.features.follow_user_feature.api.follow_user_api` → `social`
        return [module.split(".", 1)[0]]

    def get_summary(self) -> str:
        doc = self._module_doc()
        if not doc:
            return super().get_summary() or ""
        first_line = doc.strip().split("\n", 1)[0].strip()
        # Module docstrings typically start with "API: GET /path/" — strip the
        # boilerplate so the summary in Swagger reads naturally.
        if first_line.startswith("API:"):
            first_line = first_line[len("API:"):].strip()
        return first_line

    def get_description(self) -> str:
        doc = self._module_doc()
        if not doc:
            return super().get_description() or ""
        parts = doc.strip().split("\n", 1)
        return parts[1].strip() if len(parts) > 1 else ""

    def _module_doc(self) -> str | None:
        module = getmodule(self.view.__class__)
        return module.__doc__ if module else None


class XTestUserAuthScheme(OpenApiAuthenticationExtension):
    target_class = "users.authentication.XTestUserAuthentication"
    name = "XTestUserAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-Test-User-Id",
            "description": (
                "Test user id. Real authentication is intentionally out of "
                "scope (see README). Set this header to a seeded user pk "
                "(1–5 are good starting points)."
            ),
        }
