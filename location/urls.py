from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryListCreateAPIView, CountryRetrieveUpdateDestroyAPIView, CityViewSet, AirportViewSet

router = DefaultRouter()

router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)


urlpatterns = [
    path("", include(router.urls)),

    path("countries/", CountryListCreateAPIView.as_view(), name="country-list-create"),
    path("countries/<int:pk>/", CountryRetrieveUpdateDestroyAPIView.as_view(), name="country-detail"),
]
