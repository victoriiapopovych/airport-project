from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Conversation
from .serializers import ConversationListSerializer, ConversationDetailSerializer


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(user=self.request.user)
            .prefetch_related("messages")
            .order_by("-updated_at")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConversationDetailSerializer

        return ConversationListSerializer
    

from django.shortcuts import render


def chat_test_page(request):
    return render(request, "chat/test_chat.html")