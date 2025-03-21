from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    audio = models.FileField(upload_to='chat_audio/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.content:
            return f"{self.user.username}: {self.content[:50]}"
        elif self.audio:
            return f"{self.user.username}: [Voice message]"
        else:
            return f"{self.user.username}: [Image]"


class ChatMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]

    chat = models.ForeignKey(Chat, related_name="members", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="chats", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat', 'user')

    def __str__(self):
        return f"{self.user.username} ({self.role}) in {self.chat.name}"


class ChatInvitation(models.Model):
    chat = models.ForeignKey(Chat, related_name="invitations", on_delete=models.CASCADE)
    inviter = models.ForeignKey(User, related_name="sent_invitations", on_delete=models.CASCADE)
    invitee = models.ForeignKey(User, related_name="received_invitations", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(null=True)

    class Meta:
        unique_together = ("chat", "invitee")

    def __str__(self):
        return f"{self.inviter.username} invited {self.invitee.username} to {self.chat.name}"
