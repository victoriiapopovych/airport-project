from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoungeViewSet, LoungeAccessViewSet


router = DefaultRouter()

router.register("lounges", LoungeViewSet)
router.register("lounge-accesses", LoungeAccessViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
