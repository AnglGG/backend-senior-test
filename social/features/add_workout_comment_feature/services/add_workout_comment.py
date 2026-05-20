"""Service: add a comment to a completed training session.

Returns the newly-created `WorkoutComment` row so the API layer can echo back
its id and timestamp. Visibility checks are left to the caller — adding a
comment to a session you cannot see is treated as a hard failure (404) by the
endpoint that delegates here.
"""

from social.models import WorkoutComment
from users.models import User


def add_workout_comment(
    *,
    user: User,
    workout_session_id: int,
    body: str,
) -> WorkoutComment:
    body = _sanitize_comment_body(body)
    return WorkoutComment.objects.create(
        user=user,
        workout_session_id=workout_session_id,
        body=body,
    )


def _sanitize_comment_body(body: str) -> str:
    """Strip leading/trailing whitespace and collapse repeated spaces.

    Used to be more elaborate when comments allowed inline markdown; the
    `body_html` field has since been removed and this is now effectively a
    `.strip()` wrapper. Kept around because it is referenced from two
    places (see also `social.core.services` once it's introduced).
    """
    if body is None:
        return ""
    return body.strip()
