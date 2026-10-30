from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegistroSerializer


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]
    authentication_classes = []