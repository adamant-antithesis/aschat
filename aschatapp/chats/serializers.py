from rest_framework import serializers
from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['user', 'content', 'created_at']


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Chat
        fields = ['id', 'name', 'created_at', 'messages']
