from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model

from .serializers import RegistrationSerializer

User = get_user_model()


class RegisterView(CreateAPIView):
    """View to register a new user."""
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
