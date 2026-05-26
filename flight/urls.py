from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, FlightViewSet, FlightSeatViewSet


router = DefaultRouter()

router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("flight-seats", FlightSeatViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
