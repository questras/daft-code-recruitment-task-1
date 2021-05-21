from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication

from .models import ShortMessage
from .serializers import ShortMessageSerializer


class ShortMessageViewSet(ModelViewSet):
    """View set for endpoints to perform operations on
    `ShortMessage` instances.
    It allows to:
    - read all messages,
    - read specific message,
    - add new message,
    - update existing message,
    - delete existing message.
    When specific message is read, its views counter is incremented.
    Once a message is update, its views counter is reset (set to 0).
    """
    queryset = ShortMessage.objects.all()
    serializer_class = ShortMessageSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def retrieve(self, request, *args, **kwargs):
        message = self.get_object()
        message.increment_views()

        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        # Reset views counter on update.
        serializer.save(views_counter=0)
