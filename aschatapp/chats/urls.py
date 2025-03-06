from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ChatViewSet, MessageViewSet


router = SimpleRouter()
router.register(r'chats', ChatViewSet, basename='chat')

chats_router = SimpleRouter()
chats_router.register(r'(?P<chat_id>[^/.]+)/messages', MessageViewSet, basename='chat-messages')


urlpatterns = [
    path('', include(router.urls)),
    path('chats/', include(chats_router.urls)),
]
