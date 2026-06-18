from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ConversationViewSet, chat_test_page

router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversation")

urlpatterns = [
    path("test/", chat_test_page, name="chat-test"),
]

urlpatterns += router.urls