from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import ShortMessageViewSet

# Router providing urls for endpoints provided
# by `ShortMessageViewSet`.
short_messages_router = DefaultRouter()
short_messages_router.register('short_messages', ShortMessageViewSet)

urlpatterns = [
    path('', include(short_messages_router.urls)),
]
