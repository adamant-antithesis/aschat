from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ChatViewSet, MessageViewSet


router = SimpleRouter()
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')


urlpatterns = [
    path('', include(router.urls)),
]
