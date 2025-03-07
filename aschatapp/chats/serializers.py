from rest_framework import serializers
from .models import Chat, Message, ChatInvitation
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'name', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user')

    class Meta:
        model = Message
        fields = ['id', 'chat', 'user', 'user_id', 'content', 'created_at']


class ChatInvitationSerializer(serializers.ModelSerializer):
    inviter = serializers.StringRelatedField()
    invitee = serializers.StringRelatedField()
    inviter_id = serializers.IntegerField(source='inviter.id')
    invitee_id = serializers.IntegerField(source='invitee.id')

    class Meta:
        model = ChatInvitation
        fields = ["id", "chat", "inviter", "inviter_id", "invitee", "invitee_id", "created_at", "accepted"]
