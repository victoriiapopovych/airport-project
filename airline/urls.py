from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AirlineViewSet, AirplaneTypeViewSet, AirplaneViewSet


router = DefaultRouter()

router.register("airlines", AirlineViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
