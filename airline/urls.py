from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AirlineViewSet, AirplaneTypeListCreateAPIView, AirplaneTypeRetrieveUpdateDestroyAPIView, AirplaneViewSet, SeatClassViewSet, AirplaneSeatViewSet


router = DefaultRouter()

router.register("airlines", AirlineViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("seat-classes", SeatClassViewSet)
router.register("airplane-seats", AirplaneSeatViewSet)


urlpatterns = [
    path("", include(router.urls)),

    path("airplane-types/", AirplaneTypeListCreateAPIView.as_view(), name="airplane-type-list-create"),
    path("airplane-types/<int:pk>/", AirplaneTypeRetrieveUpdateDestroyAPIView.as_view(),name="airplane-type-detail",),
]
