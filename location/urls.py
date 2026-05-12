from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, CityViewSet, AirportViewSet

router = DefaultRouter()

router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
