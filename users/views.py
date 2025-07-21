from rest_framework import generics

from users.models import CustomUser
from users.serializers import CustomUserSerializer


class CustomUserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CustomUserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = CustomUserSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
