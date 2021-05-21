from rest_framework import serializers

from .models import ShortMessage


class ShortMessageSerializer(serializers.ModelSerializer):
    """Serializer for `ShortMessage` class that allows
    to specify body of the message and to read id, body and views
    counter of the message."""

    class Meta:
        model = ShortMessage
        fields = ('id', 'body', 'views_counter')
        read_only_fields = ('id', 'views_counter',)
