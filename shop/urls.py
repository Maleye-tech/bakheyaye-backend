from django.http import JsonResponse
from django.urls import include, path
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CategoryViewSet, MeView, MetaView, TenueViewSet

class LoginView(TokenObtainPairView):
    """Connexion JWT, limitée à 10 essais par minute (anti force brute)."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


def health(_request):
    """Pour un ping de surveillance (garde le service éveillé)."""
    return JsonResponse({"status": "ok"})


router = DefaultRouter()
router.register("tenues", TenueViewSet, basename="tenue")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/token/", LoginView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("meta/", MetaView.as_view(), name="meta"),
    path("", include(router.urls)),
]
