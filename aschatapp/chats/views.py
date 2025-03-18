from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.parsers import MultiPartParser, FormParser
import logging

from .models import Chat, Message, ChatMember, ChatInvitation
from .serializers import ChatSerializer, MessageSerializer, ChatInvitationSerializer

logger = logging.getLogger(__name__)


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if Chat.objects.filter(name=serializer.validated_data['name']).exists():
            raise ValidationError({"detail": "Chat with this name already exists."})
        chat = serializer.save()
        ChatMember.objects.create(chat=chat, user=self.request.user, role='admin')

    @action(detail=True, methods=["patch"], url_path="role")
    def set_role(self, request, pk=None):
        chat = self.get_object()
        admin = request.user
        user_id = request.data.get("user_id")
        new_role = request.data.get("role")

        if new_role not in ["admin", "moderator", "member"]:
            return Response({"detail": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST)

        if not ChatMember.objects.filter(chat=chat, user=admin, role="admin").exists():
            raise PermissionDenied("Only chat admins can change roles.")

        try:
            member = ChatMember.objects.get(chat=chat, user_id=user_id)
        except ChatMember.DoesNotExist:
            raise NotFound("User is not a member of this chat.")

        if member.role == "admin" and new_role != "admin":
            if ChatMember.objects.filter(chat=chat, role="admin").count() == 1:
                return Response({"detail": "Cannot remove the last admin."}, status=status.HTTP_400_BAD_REQUEST)

        member.role = new_role
        member.save()

        return Response({"detail": f"User {member.user.username} is now {new_role}."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def details(self, request, pk=None):
        user = request.user
        chat = self.get_object()

        if not ChatMember.objects.filter(chat=chat, user=user).exists():
            raise PermissionDenied("You are not a member of this chat.")

        chat_serializer = self.get_serializer(chat)
        messages = Message.objects.filter(chat=chat).order_by("created_at")
        message_serializer = MessageSerializer(
            messages,
            many=True,
            context={'request': request}
        )
        
        logger.info(f"Returning {len(messages)} messages for chat {pk}")
        for msg in message_serializer.data:
            if msg.get('image'):
                logger.info(f"Message {msg['id']} has image: {msg['image']}")
                logger.info(f"Full message data: {msg}")

        return Response({
            "chat": chat_serializer.data,
            "messages": message_serializer.data
        })

    @action(detail=True, methods=["post"])
    def invite(self, request, pk=None):
        chat = self.get_object()
        inviter = request.user
        user_id = request.data.get("user_id")

        if not ChatMember.objects.filter(chat=chat, user=inviter).exists():
            raise PermissionDenied("You must be a member of this chat to invite others.")

        try:
            user_to_invite = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if ChatInvitation.objects.filter(chat=chat, invitee=user_to_invite).exists():
            return Response({"detail": "User has already been invited to this chat."},
                            status=status.HTTP_400_BAD_REQUEST)

        if ChatMember.objects.filter(chat=chat, user=user_to_invite).exists():
            return Response({"detail": "User is already a member of this chat."},
                            status=status.HTTP_400_BAD_REQUEST)

        ChatInvitation.objects.create(chat=chat, inviter=inviter, invitee=user_to_invite)

        return Response({"detail": f"{user_to_invite.username} has been invited to the chat."},
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def invitations(self, request, pk=None):
        chat = self.get_object()

        if not ChatMember.objects.filter(chat=chat, user=request.user).exists():
            raise PermissionDenied("You must be a member of this chat to see invitations.")

        invitations = ChatInvitation.objects.filter(chat=chat)
        serializer = ChatInvitationSerializer(invitations, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path='invitations/(?P<invite_id>\d+)')
    def respond_invite(self, request, pk=None, invite_id=None):
        chat = self.get_object()
        invitee = request.user

        accepted = request.data.get('accepted', None)

        if accepted is None:
            return Response({"detail": "You must provide 'accepted' value (true or false)."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = ChatInvitation.objects.get(id=invite_id, chat=chat, invitee=invitee, accepted=None)
        except ChatInvitation.DoesNotExist:
            raise NotFound("No pending invitation found")

        invitation.accepted = accepted
        invitation.save()

        if accepted:
            ChatMember.objects.create(chat=chat, user=invitee)
            return Response({"detail": "Invitation accepted"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invitation rejected"}, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        user = self.request.user

        if not ChatMember.objects.filter(chat_id=chat_id, user=user).exists():
            return Message.objects.none()

        return self.queryset.filter(chat__id=chat_id).order_by("created_at")

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = Chat.objects.get(id=chat_id)
        
        image = self.request.FILES.get('image')
        if image:
            serializer.save(chat=chat, user=self.request.user, image=image)
        else:
            serializer.save(chat=chat, user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        chat = message.chat
        user = request.user

        is_moderator = ChatMember.objects.filter(chat=chat, user=user, role__in=['admin', 'moderator']).exists()

        if message.user == user or is_moderator:
            if message.image:
                message.image.delete()
            self.perform_destroy(message)
            return Response({"detail": "Message deleted."}, status=status.HTTP_204_NO_CONTENT)

        raise PermissionDenied("You don't have permission to delete this message.")
