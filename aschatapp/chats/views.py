from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Chat, Message, ChatMember
from .serializers import ChatSerializer, MessageSerializer


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        chat = serializer.save()
        ChatMember.objects.create(chat=chat, user=self.request.user)

    @action(detail=True, methods=["get"])
    def details(self, request, pk=None):
        user = request.user
        chat = self.get_object()

        if not ChatMember.objects.filter(chat=chat, user=user).exists():
            raise PermissionDenied("You are not a member of this chat.")

        chat_serializer = self.get_serializer(chat)
        messages = Message.objects.filter(chat=chat).order_by("created_at")
        message_serializer = MessageSerializer(messages, many=True)

        return Response({
            "chat": chat_serializer.data,
            "messages": message_serializer.data
        })


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        user = self.request.user

        if not ChatMember.objects.filter(chat_id=chat_id, user=user).exists():
            return Message.objects.none()

        return self.queryset.filter(chat__id=chat_id).order_by("created_at")

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = Chat.objects.get(id=chat_id)

        serializer.save(chat=chat, user=self.request.user)
