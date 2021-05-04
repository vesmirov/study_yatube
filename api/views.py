from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins

from .serializers import UserSerializer

User = get_user_model()


class UserModelViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

