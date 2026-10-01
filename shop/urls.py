from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CategoryViewSet, MeView, MetaView, TenueViewSet

router = DefaultRouter()
router.register("tenues", TenueViewSet, basename="tenue")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("meta/", MetaView.as_view(), name="meta"),
    path("", include(router.urls)),
]
