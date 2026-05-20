"""Root URL configuration for Symmetry Lite."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("exercises/", include("exercise_catalog.core.apis.urls", namespace="exercise_catalog")),
    path("workouts/", include("workout_sessions.core.apis.urls", namespace="workout_sessions")),
    path("workout-plans/", include("workout_plans.core.apis.urls", namespace="workout_plans")),
    path("users/", include("users.core.apis.urls", namespace="users")),
]
