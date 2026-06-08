from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, FlightViewSet


router = DefaultRouter()

router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
