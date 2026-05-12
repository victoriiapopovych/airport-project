from rest_framework import viewsets
from .models import Lounge, LoungeAccess
from .serializers import LoungeSerializer, LoungeAccessSerializer


class LoungeViewSet(viewsets.ModelViewSet):
    queryset = Lounge.objects.all()
    serializer_class = LoungeSerializer


class LoungeAccessViewSet(viewsets.ModelViewSet):
    queryset = LoungeAccess.objects.all()
    serializer_class = LoungeAccessSerializer
