from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterAPIView


router = DefaultRouter()

router.register("users", UserViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterAPIView.as_view(), name="user-register"),
]
